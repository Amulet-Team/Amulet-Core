from __future__ import annotations

from typing import Tuple, Any, Union, Generator, Dict, TYPE_CHECKING
import copy
import numpy

import PyMCTranslate

from amulet import log
from amulet.world_interface.chunk import interfaces
from amulet.api.errors import (
    ChunkLoadError,
    ChunkDoesNotExist,
    ObjectReadWriteError,
)
from amulet.api.block import BlockManager

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface
    from amulet.api.chunk import Chunk
    from amulet.api.wrapper.chunk.translator import Translator, VersionIdentifierType


class FormatWraper:
    """
    The Format class is a class that sits between the serialised world or structure data and the program using amulet-core.
    The Format class is used to access chunks from the serialised source in the universal format and write them back again.
    The BaseFormat class holds the common methods shared by the sub-classes.
    """
    def __init__(self, path: str):
        self._path = path
        self._translation_manager = None
        self._version = None
        self._changed: bool = False

    @property
    def readable(self) -> bool:
        """Can this object have data read from it."""
        return True

    @property
    def writeable(self) -> bool:
        """Can this object have data written to it."""
        return True

    @property
    def translation_manager(self) -> PyMCTranslate.TranslationManager:
        """The translation manager attached to the world"""
        if self._translation_manager is None:
            self._translation_manager = PyMCTranslate.new_translation_manager()
        return self._translation_manager

    @translation_manager.setter
    def translation_manager(self, value: PyMCTranslate.TranslationManager):
        self._translation_manager = value

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        Returns whether this format is able to load the given object.

        :param path: The path of the object to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        raise NotImplementedError()

    @property
    def platform(self) -> str:
        """Platform string ("bedrock" / "java" / ...)"""
        raise NotImplementedError

    @property
    def version(self) -> Union[int, Tuple[int, ...]]:
        """Platform string ("bedrock" / "java" / ...)"""
        if self._version is None:
            self._version = self._get_version()
        return self._version

    def _get_version(self) -> Union[int, Tuple[int, ...]]:
        raise NotImplementedError

    @property
    def max_world_version(self) -> Tuple[str, Union[int, Tuple[int, ...]]]:
        """The version the world was last opened in
        This should be greater than or equal to the chunk versions found within"""
        return self.platform, self.version

    @property
    def changed(self) -> bool:
        return self._changed

    @property
    def path(self) -> str:
        """The path to the world directory"""
        return self._path

    def _get_interface(
        self, max_world_version, raw_chunk_data=None
    ) -> 'Interface':
        if raw_chunk_data:
            key = self._get_interface_key(raw_chunk_data)
        else:
            key = max_world_version
        return interfaces.loader.get(key)

    def _get_interface_and_translator(self, max_world_version, raw_chunk_data=None) -> Tuple['Interface', 'Translator', 'VersionIdentifierType']:
        interface = self._get_interface(max_world_version, raw_chunk_data)
        translator, version_identifier = interface.get_translator(self.max_world_version, raw_chunk_data)
        return interface, translator, version_identifier

    def _get_interface_key(self, raw_chunk_data) -> Any:
        raise NotImplementedError

    def open(self):
        """Open the database for reading and writing"""
        raise NotImplementedError

    @property
    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        raise NotImplementedError

    def _verify_has_lock(self):
        """Ensure that the Format has a lock on the world. Throw WorldAccessException if not"""
        if not self.has_lock:
            raise ObjectReadWriteError(
                "The world has been opened somewhere else or the .open() method was not called"
            )

    def save(self):
        """Save the data back to the disk database"""
        raise NotImplementedError

    def close(self):
        """Close the disk database"""
        raise NotImplementedError

    def unload(self):
        """Unload data stored in the Format class"""
        raise NotImplementedError

    def all_chunk_coords(self, *args) -> Generator[Tuple[int, int]]:
        """A generator of all chunk coords"""
        raise NotImplementedError

    def load_chunk(
        self, cx: int, cz: int, global_palette: BlockManager, *args
    ) -> 'Chunk':
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param global_palette: The universal block manager
        :return: The chunk at the given coordinates.
        """
        if not self.readable:
            raise ChunkLoadError('This object is not readable')
        try:
            return self._load_chunk(cx, cz, global_palette, *args)
        except ChunkDoesNotExist as e:
            raise e
        except Exception:
            log.error(f"Error loading chunk {cx} {cz}", exc_info=True)
            raise ChunkLoadError

    def _load_chunk(
        self,
        cx: int,
        cz: int,
        global_palette: BlockManager,
        *args,
        recurse: bool = True
    ) -> 'Chunk':
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param global_palette: The universal block manager
        :param recurse: bool: look in boundary chunks if required to fully define data
        :return: The chunk at the given coordinates.
        """

        # Gets an interface (the code that actually reads the chunk data)
        raw_chunk_data = self._get_raw_chunk_data(cx, cz, *args)
        interface, translator, game_version = self._get_interface_and_translator(self.max_world_version, raw_chunk_data)

        # decode the raw chunk data into the universal format
        chunk, chunk_palette = interface.decode(cx, cz, raw_chunk_data)

        # set up a callback that translator can use to get chunk data
        if recurse:
            chunk_cache: Dict[Tuple[int, int], Tuple['Chunk', BlockManager]] = {}

            def get_chunk_callback(x: int, z: int) -> Tuple['Chunk', BlockManager]:
                palette = BlockManager()
                cx_, cz_ = cx + x, cz + z
                if (cx_, cz_) not in chunk_cache:
                    chunk_ = self._load_chunk(cx_, cz_, palette, *args, False)
                    chunk_cache[(cx_, cz_)] = chunk_, palette
                return chunk_cache[(cx_, cz_)]

        else:
            get_chunk_callback = None

        # translate the data to universal format
        chunk, chunk_palette = translator.to_universal(
            game_version,
            self.translation_manager,
            chunk,
            chunk_palette,
            get_chunk_callback,
            recurse,
        )

        # convert the block numerical ids from local chunk palette to global palette
        chunk_to_global = numpy.array(
            [global_palette.get_add_block(block) for block in chunk_palette],
            dtype=numpy.uint,
        )
        for cy in chunk.blocks.sub_chunks:
            chunk.blocks.add_sub_chunk(cy, chunk_to_global[chunk.blocks.get_sub_chunk(cy)])
        chunk.changed = False
        return chunk

    def commit_chunk(
        self, chunk: 'Chunk', global_palette: BlockManager, *args
    ):
        """
        Save a universal format chunk to the Format database (not the disk database)
        call save method to write changed chunks back to the disk database
        :param chunk: The chunk object to translate and save
        :param global_palette: The universal block manager
        :return:
        """
        if not self.writeable:
            log.error('This object is not writeable')
            return
        try:
            self._commit_chunk(copy.deepcopy(chunk), global_palette, *args)
        except Exception:
            log.error(f"Error saving chunk {chunk}", exc_info=True)
        self._changed = True

    def _commit_chunk(
        self,
        chunk: 'Chunk',
        global_palette: BlockManager,
        *args,
        recurse: bool = True,
    ):
        """
        Saves a universal amulet.api.chunk.Chunk object
        Calls the interface then the translator.
        It then calls _put_chunk_data to store the data returned by the interface
        """
        # get the coordinates for later
        cx, cz = chunk.cx, chunk.cz

        # Gets an interface, translator and most recent chunk version for the game version.
        interface, translator, chunk_version = self._get_interface_and_translator(self.max_world_version)

        chunk, chunk_palette = self._convert_to_save(chunk, global_palette, chunk_version, translator, recurse)
        raw_chunk_data = self._encode(chunk, chunk_palette, interface)

        self._put_raw_chunk_data(cx, cz, raw_chunk_data, *args)

    def _convert_to_save(
            self,
            chunk: Chunk,
            global_palette: BlockManager,
            chunk_version,
            translator,
            recurse: bool = True
    ) -> Tuple[Chunk, numpy.ndarray]:
        # convert the global indexes into local indexes and a local palette
        palette = []
        palette_len = 0
        for cy in chunk.blocks.sub_chunks:
            sub_chunk_palette, sub_chunk = numpy.unique(chunk.blocks.get_sub_chunk(cy), return_inverse=True)
            chunk.blocks.add_sub_chunk(cy, sub_chunk.reshape((16, 16, 16)) + palette_len)
            palette_len += len(sub_chunk_palette)
            palette.append(sub_chunk_palette)

        if palette:
            chunk_palette, lut = numpy.unique(numpy.concatenate(palette), return_inverse=True)
            for cy in chunk.blocks.sub_chunks:
                chunk.blocks.add_sub_chunk(cy, lut[chunk.blocks.get_sub_chunk(cy)])
            chunk_palette = numpy.vectorize(global_palette.__getitem__)(chunk_palette)
        else:
            chunk_palette = numpy.array([], dtype=numpy.object)

        def get_chunk_callback(_: int, __: int) -> Tuple['Chunk', numpy.ndarray]:
            # conversion from universal should not require any data outside the block
            return chunk, numpy.array(global_palette.blocks())

        # translate from universal format to version format
        return translator.from_universal(
            chunk_version,
            self.translation_manager,
            chunk,
            chunk_palette,
            get_chunk_callback,
            recurse,
        )

    def _encode(self, chunk: Chunk, chunk_palette: numpy.ndarray, interface: Interface):
        return interface.encode(
            chunk, chunk_palette, self.max_world_version
        )

    def delete_chunk(self, cx: int, cz: int, *args):
        raise NotImplementedError

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, *args):
        """
        Actually stores the data from the interface to disk.
        """
        raise NotImplementedError()

    def _get_raw_chunk_data(self, cx: int, cz: int, *args) -> Any:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The raw chunk data.
        """
        raise NotImplementedError()

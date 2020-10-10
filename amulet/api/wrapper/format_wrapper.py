from __future__ import annotations

from typing import Tuple, Any, Generator, Dict, List, Optional, TYPE_CHECKING
import copy
import numpy
import os
import shutil

import PyMCTranslate

from amulet import log
from amulet.api.registry import BlockManager
from amulet.api.errors import (
    ChunkLoadError,
    ChunkDoesNotExist,
    ObjectReadError,
    ObjectReadWriteError,
)
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    ChunkCoordinates,
    Dimension,
    PlatformType,
    VersionIdentifierType,
)
from amulet.api.selection import SelectionGroup, SelectionBox

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface
    from amulet.api.chunk import Chunk
    from amulet.api.wrapper.chunk.translator import Translator


DefaultPlatform = "Unknown Platform"
DefaultVersion = (0, 0, 0)


class FormatWrapper:
    """
    The Format class is a class that sits between the serialised world or structure data and the program using amulet-core.
    The Format class is used to access chunks from the serialised source in the universal format and write them back again.
    The FormatWrapper class holds the common methods shared by the sub-classes.
    """

    def __init__(self, path: str):
        if type(self) is FormatWrapper:
            raise Exception(
                "FormatWrapper is not directly usable. One of its subclasses must be used."
            )
        self._path = path
        self._is_open = False
        self._has_lock = False
        self._translation_manager = None
        self._platform: Optional[PlatformType] = DefaultPlatform
        self._version: Optional[VersionNumberAny] = DefaultVersion
        self._selection = SelectionGroup(
            [
                SelectionBox(
                    (-30_000_000, 0, -30_000_000), (30_000_000, 256, 30_000_000),
                )
            ]
        )
        self._changed: bool = False

    @property
    def sub_chunk_size(self) -> int:
        return 16

    @property
    def path(self) -> str:
        """The path to the data on disk."""
        return self._path

    @property
    def readable(self) -> bool:  # TODO: remove this. FormatWrappers should be simultaneously readable and writable.
        """Can this object have data read from it."""
        return True

    @property
    def writeable(self) -> bool:  # TODO: remove this. FormatWrappers should be simultaneously readable and writable.
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
        # TODO: this should not be settable.
        self._translation_manager = value

    @property
    def exists(self) -> bool:
        """Does some data exist at the specified path."""
        return os.path.exists(self.path)

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        Returns whether this format is able to load the given object.

        :param path: The path of the object to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        raise NotImplementedError

    @property
    def valid_formats(self) -> Tuple[Tuple[PlatformType, bool, bool], ...]:
        """The valid platform and version combinations that this object can accept.
        This is used when setting the platform and version in the create_and_open method
        to verify that the platform and version are valid.

        :return: A tuple of tuples containing the platform followed by two booleans to determine if numerical and blockstate are valid respectively
        """
        raise NotImplementedError

    @property
    def platform(self) -> PlatformType:
        """Platform string the data is stored in (eg "bedrock" / "java" / ...)"""
        return self._platform

    @property
    def version(self) -> VersionNumberAny:
        """The version number for the given platform the data is stored in eg (1, 16, 2)"""
        return self._version

    @property
    def max_world_version(self) -> VersionIdentifierType:
        """The version the world was last opened in
        This should be greater than or equal to the chunk versions found within"""
        return self.platform, self.version

    @property
    def changed(self) -> bool:
        return self._changed

    @property
    def dimensions(self) -> List[Dimension]:
        """A list of all the dimensions contained in the world"""
        raise NotImplementedError

    @property
    def can_add_dimension(self) -> bool:
        """Can external code register a new dimension.
        If False register_dimension will have no effect."""
        raise NotImplementedError

    def register_dimension(self, dimension_internal: Any, dimension_name: Dimension):
        """
        Register a new dimension.
        :param dimension_internal: The internal representation of the dimension
        :param dimension_name: The name of the dimension shown to the user
        :return:
        """
        raise NotImplementedError

    @property
    def requires_selection(self) -> bool:
        """Does this object require that a selection be defined when creating it from scratch?"""
        return False

    @property
    def multi_selection(self) -> bool:
        """Does this object support having multiple selection boxes."""
        return False

    @property
    def selection(self) -> SelectionGroup:
        """The area that all chunk data must fit within."""
        return self._selection.copy()

    def _get_interface(self, max_world_version, raw_chunk_data=None) -> "Interface":
        raise NotImplementedError

    def _get_interface_and_translator(
        self, max_world_version, raw_chunk_data=None
    ) -> Tuple["Interface", "Translator", "VersionNumberAny"]:
        interface = self._get_interface(max_world_version, raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            self.max_world_version, raw_chunk_data
        )
        return interface, translator, version_identifier

    def create_and_open(
        self,
        platform: PlatformType,
        version: VersionNumberAny,
        selection: Optional[SelectionGroup] = None,
    ):
        """Remove the data at the path and set up a new database.
        You might want to call FormatWrapper.exists to check if something exists at the path
        and warn the user they are going to overwrite existing data before calling this method."""
        if self.is_open:
            raise ObjectReadError(f"Cannot open {self} because it was already opened.")
        if os.path.isdir(self.path):
            shutil.rmtree(self.path, ignore_errors=True)
        self._create_and_open(platform, version, selection)
        self._is_open = True
        self._has_lock = True

    def _create_and_open(
        self,
        platform: PlatformType,
        version: VersionNumberAny,
        selection: Optional[SelectionGroup] = None,
    ):
        """Set up the database from scratch."""
        raise NotImplementedError

    def open(self):
        """Open the database for reading and writing"""
        if self.is_open:
            raise ObjectReadError(f"Cannot open {self} because it was already opened.")
        self._open()
        self._is_open = True
        self._has_lock = True

    def _open(self):
        raise NotImplementedError

    @property
    def is_open(self):
        """Has the object been opened."""
        return self._is_open

    @property
    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        return self._has_lock

    def _verify_has_lock(self):
        """Ensure that the FormatWrapper is open and has a lock on the object.

        :return: None
        :raises: ObjectReadWriteError if the FormatWrapper does not have a lock on the object.
        """
        if not self.is_open:
            raise ObjectReadWriteError(f"The object {self} was never opened. Call .open or .create_and_open to open it before accessing data.")
        elif not self.has_lock:
            raise ObjectReadWriteError(
                f"The lock on the object {self} has been lost. It was probably opened somewhere else."
            )

    def save(self):
        """Save the data back to the disk database"""
        self._verify_has_lock()
        self._save()
        self._changed = False

    def _save(self):
        raise NotImplementedError

    def close(self):
        """Close the disk database"""
        if self.is_open:
            self._is_open = False
            self._has_lock = False
            self._close()

    def _close(self):
        raise NotImplementedError

    def unload(self):
        """Unload data stored in the Format class"""
        raise NotImplementedError

    def all_chunk_coords(
        self, dimension: Dimension
    ) -> Generator[ChunkCoordinates, None, None]:
        """A generator of all chunk coords in the given dimension"""
        raise NotImplementedError

    def load_chunk(self, cx: int, cz: int, dimension: Dimension) -> "Chunk":
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the chunk from.
        :return: The chunk at the given coordinates.
        :raises: ChunkLoadError or ChunkDoesNotExist as is relevant.
        """
        if not self.readable:
            raise ChunkLoadError("This object is not readable.")
        try:
            self._verify_has_lock()
        except ObjectReadWriteError as e:
            raise ChunkLoadError(e)
        try:
            return self._load_chunk(cx, cz, dimension)
        except ChunkDoesNotExist as e:
            raise e
        except Exception as e:
            log.error(f"Error loading chunk {cx} {cz}", exc_info=True)
            raise ChunkLoadError(e)

    def _load_chunk(
        self, cx: int, cz: int, dimension: Dimension, recurse: bool = True,
    ) -> "Chunk":
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the chunk from.
        :param recurse: bool: look in boundary chunks if required to fully define data
        :return: The chunk at the given coordinates.
        """

        # Gets an interface (the code that actually reads the chunk data)
        raw_chunk_data = self.get_raw_chunk_data(cx, cz, dimension)
        interface, translator, game_version = self._get_interface_and_translator(
            self.max_world_version, raw_chunk_data
        )

        # decode the raw chunk data into the universal format
        chunk, chunk_palette = self._decode(interface, cx, cz, raw_chunk_data)
        chunk_palette: AnyNDArray
        chunk = self._unpack(translator, game_version, chunk, chunk_palette)
        return self._convert_to_load(
            chunk, translator, game_version, dimension, recurse=recurse,
        )

    @staticmethod
    def _decode(
        interface: "Interface", cx: int, cz: int, raw_chunk_data: Any
    ) -> Tuple["Chunk", AnyNDArray]:
        return interface.decode(cx, cz, raw_chunk_data)

    def _unpack(
        self,
        translator: "Translator",
        game_version: VersionNumberAny,
        chunk: "Chunk",
        chunk_palette: AnyNDArray,
    ) -> "Chunk":
        return translator.unpack(
            game_version, self.translation_manager, chunk, chunk_palette
        )

    def _convert_to_load(
        self,
        chunk: "Chunk",
        translator: "Translator",
        game_version: VersionNumberAny,
        dimension: Dimension,
        recurse: bool = True,
    ) -> "Chunk":
        # set up a callback that translator can use to get chunk data
        cx, cz = chunk.cx, chunk.cz
        if recurse:
            chunk_cache: Dict[ChunkCoordinates, "Chunk"] = {}

            def get_chunk_callback(x: int, z: int) -> "Chunk":
                cx_, cz_ = cx + x, cz + z
                if (cx_, cz_) not in chunk_cache:
                    chunk_cache[(cx_, cz_)] = self._load_chunk(
                        cx_, cz_, dimension, recurse=False
                    )
                return chunk_cache[(cx_, cz_)]

        else:
            get_chunk_callback = None

        # translate the data to universal format
        chunk = translator.to_universal(
            game_version, self.translation_manager, chunk, get_chunk_callback, recurse,
        )

        chunk.changed = False
        return chunk

    def commit_chunk(self, chunk: "Chunk", dimension: Dimension):
        """
        Save a universal format chunk to the Format database (not the disk database)
        call save method to write changed chunks back to the disk database
        :param chunk: The chunk object to translate and save
        :param dimension: The dimension to commit the chunk to.
        :return:
        """
        if not self.writeable:
            log.error("This object is not writeable")
            return
        try:
            self._verify_has_lock()
        except ObjectReadWriteError as e:
            log.error(e)
        try:
            self._commit_chunk(copy.deepcopy(chunk), dimension)
        except Exception:
            log.error(f"Error saving chunk {chunk}", exc_info=True)
        self._changed = True

    def _commit_chunk(
        self, chunk: "Chunk", dimension: Dimension, recurse: bool = True,
    ):
        """
        Saves a universal amulet.api.chunk.Chunk object
        Calls the interface then the translator.
        It then calls _put_chunk_data to store the data returned by the interface
        """
        # get the coordinates for later
        cx, cz = chunk.cx, chunk.cz

        # Gets an interface, translator and most recent chunk version for the game version.
        interface, translator, chunk_version = self._get_interface_and_translator(
            self.max_world_version
        )

        chunk = self._convert_to_save(chunk, chunk_version, translator, recurse)
        chunk, chunk_palette = self._pack(chunk, translator, chunk_version)
        raw_chunk_data = self._encode(chunk, chunk_palette, interface)

        self.put_raw_chunk_data(cx, cz, raw_chunk_data, dimension)

    def _convert_to_save(
        self,
        chunk: "Chunk",
        chunk_version: VersionNumberAny,
        translator: "Translator",
        recurse: bool = True,
    ) -> "Chunk":
        """Convert the Chunk in Universal format to a Chunk in the version specific format."""
        # create a new streamlined block block_palette and remap the data
        palette: List[numpy.ndarray] = []
        palette_len = 0
        for cy in chunk.blocks.sub_chunks:
            sub_chunk_palette, sub_chunk = numpy.unique(
                chunk.blocks.get_sub_chunk(cy), return_inverse=True
            )
            chunk.blocks.add_sub_chunk(
                cy, sub_chunk.astype(numpy.uint32).reshape((16, 16, 16)) + palette_len
            )
            palette_len += len(sub_chunk_palette)
            palette.append(sub_chunk_palette)

        if palette:
            chunk_palette, lut = numpy.unique(
                numpy.concatenate(palette), return_inverse=True
            )
            for cy in chunk.blocks.sub_chunks:
                chunk.blocks.add_sub_chunk(
                    cy, lut.astype(numpy.uint32)[chunk.blocks.get_sub_chunk(cy)]
                )
            chunk._block_palette = BlockManager(
                numpy.vectorize(chunk.block_palette.__getitem__)(chunk_palette)
            )
        else:
            chunk._block_palette = BlockManager()

        def get_chunk_callback(_: int, __: int) -> "Chunk":
            # conversion from universal should not require any data outside the block
            return chunk

        # translate from universal format to version format
        return translator.from_universal(
            chunk_version, self.translation_manager, chunk, get_chunk_callback, recurse,
        )

    def _pack(
        self, chunk: "Chunk", translator: "Translator", chunk_version: VersionNumberAny,
    ) -> Tuple["Chunk", AnyNDArray]:
        """Pack the chunk data into the format required by the encoder.
        This includes converting the string names to numerical formats for the versions that require it."""
        return translator.pack(chunk_version, self.translation_manager, chunk)

    def _encode(
        self, chunk: "Chunk", chunk_palette: AnyNDArray, interface: "Interface"
    ) -> Any:
        """Encode the data to the raw format as saved on disk."""
        return interface.encode(chunk, chunk_palette, self.max_world_version)

    def delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        self._delete_chunk(cx, cz, dimension)
        self._changed = True

    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        raise NotImplementedError

    def put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        """
        Actually stores the data from the interface to disk.
        """
        self._verify_has_lock()
        self._put_raw_chunk_data(cx, cz, data, dimension)

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        """
        Actually stores the data from the interface to disk.
        """
        raise NotImplementedError

    def get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        self._verify_has_lock()
        return self._get_raw_chunk_data(cx, cz, dimension)

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        raise NotImplementedError

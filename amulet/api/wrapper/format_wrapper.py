from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Tuple,
    Any,
    Generator,
    Dict,
    List,
    Optional,
    TYPE_CHECKING,
    Iterable,
    Callable,
    Type,
    Union,
    TypeVar,
    Generic,
)
import copy
import numpy
import os
import warnings
import logging

import PyMCTranslate

from amulet.api import level as api_level, wrapper as api_wrapper
from amulet.api.chunk import Chunk
from amulet.api.registry import BlockManager
from amulet.api.errors import (
    ChunkLoadError,
    ChunkDoesNotExist,
    ObjectReadError,
    ObjectReadWriteError,
    PlayerDoesNotExist,
    PlayerLoadError,
    EntryLoadError,
    EntryDoesNotExist,
    DimensionDoesNotExist,
)
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    ChunkCoordinates,
    Dimension,
    PlatformType,
)
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.player import Player

if TYPE_CHECKING:
    from amulet.api.wrapper.chunk.translator import Translator

log = logging.getLogger(__name__)

DefaultSelection = SelectionGroup(
    SelectionBox((-30_000_000, 0, -30_000_000), (30_000_000, 256, 30_000_000))
)

VersionNumberT = TypeVar("VersionNumberT", int, Tuple[int, ...])


class FormatWrapper(Generic[VersionNumberT], ABC):
    """
    The FormatWrapper class is a class that sits between the serialised world or structure data and the program using amulet-core.

    It is used to access data from the serialised source in the universal format and write them back again.
    """

    _platform: Optional[PlatformType]
    _version: Optional[VersionNumberT]

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`FormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        self._path = path
        self._is_open = False
        self._has_lock = False
        self._translation_manager = None
        self._platform = None
        self._version = None
        self._bounds: Dict[Dimension, SelectionGroup] = {}
        self._changed: bool = False

    @property
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """
        return 16

    @property
    def path(self) -> str:
        """The path to the data on disk."""
        return self._path

    @property
    @abstractmethod
    def level_name(self) -> str:
        """The name of the level."""
        raise NotImplementedError

    @property
    def translation_manager(self) -> PyMCTranslate.TranslationManager:
        """The translation manager attached to the world."""
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
    @abstractmethod
    def is_valid(path: str) -> bool:
        """
        Returns whether this format wrapper is able to load the given data.

        :param path: The path of the data to load.
        :return: True if the world can be loaded by this format wrapper, False otherwise.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        """
        The valid platform and version combinations that this object can accept.

        This is used when setting the platform and version in the create_and_open method
        to verify that the platform and version are valid.

        :return: A dictionary mapping the platform to a tuple of two booleans to determine if numerical and blockstate are valid respectively.
        """
        raise NotImplementedError

    @property
    def platform(self) -> PlatformType:
        """Platform string the data is stored in (eg "bedrock" / "java" / ...)"""
        if self._platform is None:
            raise Exception(
                "Cannot access the game platform until the level has been loaded."
            )
        return self._platform

    @property
    def version(self) -> VersionNumberT:
        """The version number for the given platform the data is stored in eg (1, 16, 2)"""
        if self._version is None:
            raise Exception(
                "Cannot access the game version until the level has been loaded."
            )
        return self._version

    @property
    def max_world_version(self) -> Tuple[PlatformType, VersionNumberT]:
        """
        The version the world was last opened in.

        This should be greater than or equal to the chunk versions found within.
        """
        return self.platform, self.version

    @property
    def changed(self) -> bool:
        """Has any data been pushed to the format wrapper that has not been saved to disk."""
        return self._changed

    @property
    @abstractmethod
    def dimensions(self) -> List[Dimension]:
        """A list of all the dimensions contained in the world."""
        raise NotImplementedError

    @property
    @abstractmethod
    def can_add_dimension(self) -> bool:
        """
        Can external code register a new dimension.

        If False :meth:`register_dimension` will have no effect.
        """
        raise NotImplementedError

    @abstractmethod
    def register_dimension(self, dimension_identifier: Any):
        """
        Register a new dimension.

        :param dimension_identifier: The identifier for the dimension.
        """
        raise NotImplementedError

    @property
    def requires_selection(self) -> bool:
        """Does this object require that a selection be defined when creating it from scratch?"""
        return False

    @property
    def multi_selection(self) -> bool:
        """
        Does this object support having multiple selection boxes.

        If False it will be given exactly 1 selection.

        If True can be given 0 or more.
        """
        return False

    @property
    def selection(self) -> SelectionGroup:
        """The area that all chunk data must fit within."""
        warnings.warn(
            "FormatWrapper.selection is depreciated and will be removed in the future. Please use FormatWrapper.bounds(dimension) instead",
            DeprecationWarning,
        )
        return self.bounds(self.dimensions[0])

    def bounds(self, dimension: Dimension) -> SelectionGroup:
        if dimension not in self._bounds:
            if dimension in self.dimensions:
                raise Exception(
                    f'The dimension exists but there is not selection registered for it. Please report this to a developer "{dimension}" {self}'
                )
            else:
                raise DimensionDoesNotExist
        return self._bounds[dimension]

    @abstractmethod
    def _get_interface(
        self, raw_chunk_data: Optional[Any] = None
    ) -> api_wrapper.Interface:
        raise NotImplementedError

    def _get_interface_and_translator(
        self, raw_chunk_data=None
    ) -> Tuple[api_wrapper.Interface, "Translator", VersionNumberAny]:
        interface = self._get_interface(raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            self.max_world_version, raw_chunk_data
        )
        return interface, translator, version_identifier

    def create_and_open(
        self,
        platform: PlatformType,
        version: VersionNumberAny,
        bounds: Union[
            SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None
        ] = None,
        overwrite: bool = False,
        **kwargs,
    ):
        """
        Remove the data at the path and set up a new database.

        You might want to call :attr:`exists` to check if something exists at the path
        and warn the user they are going to overwrite existing data before calling this method.

        :param platform: The platform the data should use.
        :param version: The version the data should use.
        :param bounds: The bounds for each dimension. If one :class:`SelectionGroup` is given it will be applied to all dimensions.
        :param overwrite: Should an existing database be overwritten. If this is False and one exists and error will be thrown.
        :param kwargs: Extra arguments as each implementation requires.
        :return:
        """
        if self.is_open:
            raise ObjectReadError(f"Cannot open {self} because it was already opened.")

        if (
            platform not in self.valid_formats or len(self.valid_formats[platform]) < 2
        ):  # check that the platform and version are valid
            raise ObjectReadError(
                f"{platform} is not a valid platform for this wrapper."
            )
        translator_version = self.translation_manager.get_version(platform, version)
        if translator_version.has_abstract_format:  # numerical
            if not self.valid_formats[platform][0]:
                raise ObjectReadError(
                    f"The version given ({version}) is from the numerical format but this wrapper does not support the numerical format."
                )
        else:
            if not self.valid_formats[platform][1]:
                raise ObjectReadError(
                    f"The version given ({version}) is from the blockstate format but this wrapper does not support the blockstate format."
                )

        self._platform = translator_version.platform
        self._version = translator_version.version_number
        self._create(overwrite, bounds, **kwargs)

    def _clean_selection(self, selection: SelectionGroup) -> SelectionGroup:
        if self.multi_selection:
            return selection
        else:
            if selection:
                return SelectionGroup(
                    sorted(
                        selection.selection_boxes,
                        reverse=True,
                        key=lambda b: b.volume,
                    )[0]
                )
            else:
                raise ObjectReadError(
                    "A single selection was required but none were given."
                )

    @abstractmethod
    def _create(
        self,
        overwrite: bool,
        bounds: Union[
            SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None
        ] = None,
        **kwargs,
    ):
        """Set up the database from scratch."""
        raise NotImplementedError

    def open(self):
        """Open the database for reading and writing."""
        if self.is_open:
            raise ObjectReadError(f"Cannot open {self} because it was already opened.")
        self._open()

    @abstractmethod
    def _open(self):
        raise NotImplementedError

    @property
    def is_open(self) -> bool:
        """Has the object been opened."""
        return self._is_open

    @property
    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        return self._has_lock

    def _verify_has_lock(self):
        """
        Ensure that the FormatWrapper is open and has a lock on the object.

        :raises:
            ObjectReadWriteError: if the FormatWrapper does not have a lock on the object.
        """
        if not self.is_open:
            raise ObjectReadWriteError(
                f"The object {self} was never opened. Call .open or .create_and_open to open it before accessing data."
            )
        elif not self.has_lock:
            raise ObjectReadWriteError(
                f"The lock on the object {self} has been lost. It was probably opened somewhere else."
            )

    @staticmethod
    def pre_save_operation(level: api_level.BaseLevel) -> Generator[float, None, bool]:
        """
        Logic to run before saving. Eg recalculating height maps or lighting.

        Must be a generator that yields a number and returns a bool.

        The yielded number is the progress from 0 to 1.

        The returned bool is if changes have been made.

        :param level: The level to apply modifications to.
        :return: Have any modifications been made.
        """
        yield 1
        return False

    def save(self):
        """Save the data back to the level."""
        self._verify_has_lock()
        self._save()
        self._changed = False

    @abstractmethod
    def _save(self):
        raise NotImplementedError

    def close(self):
        """Close the level."""
        if self.is_open:
            self._is_open = False
            self._has_lock = False
            self._close()

    @abstractmethod
    def _close(self):
        raise NotImplementedError

    @abstractmethod
    def unload(self):
        """Unload data stored in the FormatWrapper class"""
        raise NotImplementedError

    @abstractmethod
    def all_chunk_coords(self, dimension: Dimension) -> Iterable[ChunkCoordinates]:
        """A generator of all chunk coords in the given dimension."""
        raise NotImplementedError

    @abstractmethod
    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        """
        Does the chunk exist in the world database?

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the chunk from.
        :return: True if the chunk exists. Calling load_chunk on this chunk may still throw ChunkLoadError
        """
        raise NotImplementedError

    def _safe_load(
        self,
        meth: Callable,
        args: Tuple[Any, ...],
        msg: str,
        load_error: Type[EntryLoadError],
        does_not_exist_error: Type[EntryDoesNotExist],
    ):
        try:
            self._verify_has_lock()
        except ObjectReadWriteError as e:
            raise does_not_exist_error(e)
        try:
            return meth(*args)
        except does_not_exist_error as e:
            raise e
        except Exception as e:
            log.error(msg.format(*args), exc_info=True)
            raise load_error(e) from e

    def load_chunk(self, cx: int, cz: int, dimension: Dimension) -> Chunk:
        """
        Loads and creates a universal :class:`~amulet.api.chunk.Chunk` object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the chunk from.
        :return: The chunk at the given coordinates.
        :raises:
            ChunkDoesNotExist: If the chunk does not exist (was deleted or never created)
            ChunkLoadError: If the chunk was not able to be loaded. Eg. If the chunk is corrupt or some error occurred when loading.
        """
        return self._safe_load(
            self._load_chunk,
            (cx, cz, dimension),
            "Error loading chunk {} {} {}",
            ChunkLoadError,
            ChunkDoesNotExist,
        )

    def _load_chunk(
        self, cx: int, cz: int, dimension: Dimension, recurse: bool = True
    ) -> Chunk:
        """
        Loads and creates a universal :class:`~amulet.api.chunk.Chunk` object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the chunk from.
        :param recurse: bool: look in boundary chunks if required to fully define data
        :return: The chunk at the given coordinates.
        """

        # Gets an interface (the code that actually reads the chunk data)
        raw_chunk_data = self._get_raw_chunk_data(cx, cz, dimension)
        interface, translator, game_version = self._get_interface_and_translator(
            raw_chunk_data
        )

        # decode the raw chunk data into the universal format
        chunk, block_palette = self._decode(
            interface, dimension, cx, cz, raw_chunk_data
        )
        block_palette: AnyNDArray
        chunk = self._unpack(translator, game_version, chunk, block_palette)
        return self._convert_to_load(
            chunk, translator, game_version, dimension, recurse=recurse
        )

    @staticmethod
    def _decode(
        interface: api_wrapper.Interface,
        dimension: Dimension,
        cx: int,
        cz: int,
        raw_chunk_data: Any,
    ) -> Tuple[Chunk, AnyNDArray]:
        return interface.decode(cx, cz, raw_chunk_data)

    def _unpack(
        self,
        translator: "Translator",
        game_version: VersionNumberAny,
        chunk: Chunk,
        block_palette: AnyNDArray,
    ) -> Chunk:
        return translator.unpack(
            game_version, self.translation_manager, chunk, block_palette
        )

    def _convert_to_load(
        self,
        chunk: Chunk,
        translator: "Translator",
        game_version: VersionNumberAny,
        dimension: Dimension,
        recurse: bool = True,
    ) -> Chunk:
        # set up a callback that translator can use to get chunk data
        cx, cz = chunk.cx, chunk.cz
        if recurse:
            chunk_cache: Dict[ChunkCoordinates, Chunk] = {}

            def get_chunk_callback(x: int, z: int) -> Chunk:
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
            game_version, self.translation_manager, chunk, get_chunk_callback, recurse
        )

        chunk.changed = False
        return chunk

    def commit_chunk(self, chunk: Chunk, dimension: Dimension):
        """
        Save a universal format chunk to the FormatWrapper database (not the level database)

        Call save method to write changed chunks back to the level.

        :param chunk: The chunk object to translate and save.
        :param dimension: The dimension to commit the chunk to.
        """
        try:
            self._verify_has_lock()
        except ObjectReadWriteError as e:
            log.error(e)
        try:
            self._commit_chunk(copy.deepcopy(chunk), dimension)
        except Exception:
            log.error(f"Error saving chunk {chunk}", exc_info=True)
        self._changed = True

    def _commit_chunk(self, chunk: Chunk, dimension: Dimension, recurse: bool = True):
        """
        Saves a universal :class:`~amulet.api.chunk.Chunk` object.

        Calls the interface then the translator.

        It then calls _put_chunk_data to store the data returned by the interface
        """
        # get the coordinates for later
        cx, cz = chunk.cx, chunk.cz

        # Gets an interface, translator and most recent chunk version for the game version.
        interface, translator, chunk_version = self._get_interface_and_translator()

        chunk = self._convert_to_save(chunk, chunk_version, translator, recurse)
        chunk, chunk_palette = self._pack(chunk, translator, chunk_version)
        raw_chunk_data = self._encode(interface, chunk, dimension, chunk_palette)

        self._put_raw_chunk_data(cx, cz, raw_chunk_data, dimension)

    def _convert_to_save(
        self,
        chunk: Chunk,
        chunk_version: VersionNumberAny,
        translator: "Translator",
        recurse: bool = True,
    ) -> Chunk:
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

        def get_chunk_callback(_: int, __: int) -> Chunk:
            # conversion from universal should not require any data outside the block
            return chunk

        # translate from universal format to version format
        return translator.from_universal(
            chunk_version, self.translation_manager, chunk, get_chunk_callback, recurse
        )

    def _pack(
        self, chunk: Chunk, translator: "Translator", chunk_version: VersionNumberAny
    ) -> Tuple[Chunk, AnyNDArray]:
        """Pack the chunk data into the format required by the encoder.
        This includes converting the string names to numerical formats for the versions that require it."""
        return translator.pack(chunk_version, self.translation_manager, chunk)

    def _encode(
        self,
        interface: api_wrapper.Interface,
        chunk: Chunk,
        dimension: Dimension,
        chunk_palette: AnyNDArray,
    ) -> Any:
        """Encode the data to the raw format as saved on disk."""
        raise NotImplementedError

    def delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        """
        Delete the given chunk from the level.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        """
        self._delete_chunk(cx, cz, dimension)
        self._changed = True

    @abstractmethod
    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        raise NotImplementedError

    def put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        """
        Commit the raw chunk data to the FormatWrapper cache.

        Call :meth:`save` to push all the cache data to the level.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param data: The raw data to commit to the level.
        :param dimension: The dimension to load the data from.
        """
        self._verify_has_lock()
        self._put_raw_chunk_data(cx, cz, data, dimension)

    @abstractmethod
    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        raise NotImplementedError

    def get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        return self._safe_load(
            self._get_raw_chunk_data,
            (cx, cz, dimension),
            "Error loading chunk {} {} {}",
            ChunkLoadError,
            ChunkDoesNotExist,
        )

    @abstractmethod
    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        raise NotImplementedError

    @abstractmethod
    def all_player_ids(self) -> Iterable[str]:
        """
        Returns a set of all player ids that are present in the level
        """
        return NotImplemented

    @abstractmethod
    def has_player(self, player_id: str) -> bool:
        """
        Test if a player id is present in the level.
        """
        return NotImplemented

    def load_player(self, player_id: str) -> "Player":
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player should be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
        return self._safe_load(
            self._load_player,
            (player_id,),
            "Error loading player {}",
            PlayerLoadError,
            PlayerDoesNotExist,
        )

    @abstractmethod
    def _load_player(self, player_id: str) -> "Player":
        """
        Get the raw player data and unpack it into a Player class.

        :param player_id: The id of the player to get.
        :return:
        """
        raise NotImplementedError

    def get_raw_player_data(self, player_id: str) -> Any:
        """
        Get the player data in the lowest level form.

        :param player_id: The id of the player to get.
        :return:
        """
        return self._safe_load(
            self._get_raw_player_data,
            (player_id,),
            "Error loading player {}",
            PlayerLoadError,
            PlayerDoesNotExist,
        )

    @abstractmethod
    def _get_raw_player_data(self, player_id: str) -> Any:
        raise NotImplementedError

import PyMCTranslate
import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amulet.api import level as api_level, wrapper as api_wrapper
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, ChunkCoordinates as ChunkCoordinates, Dimension as Dimension, PlatformType as PlatformType, VersionNumberAny as VersionNumberAny
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ChunkLoadError as ChunkLoadError, DimensionDoesNotExist as DimensionDoesNotExist, EntryDoesNotExist as EntryDoesNotExist, EntryLoadError as EntryLoadError, ObjectReadError as ObjectReadError, ObjectReadWriteError as ObjectReadWriteError, PlayerDoesNotExist as PlayerDoesNotExist, PlayerLoadError as PlayerLoadError
from amulet.api.wrapper.chunk.translator import Translator as Translator
from amulet.palette import BlockPalette as BlockPalette
from amulet.player import Player as Player
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from enum import IntEnum
from typing import Any, Callable, Dict, Generator, Generic, Iterable, List, Optional, Tuple, Type, TypeVar, Union

log: Incomplete
DefaultSelection: Incomplete
VersionNumberT = TypeVar('VersionNumberT', int, Tuple[int, ...])

class BaseFormatWrapper(ABC, Generic[VersionNumberT], metaclass=abc.ABCMeta):
    """
    The FormatWrapper class is a low level interface between the serialised data and the program using amulet-core.

    It is used to access data from the serialised source in the universal format and write them back again.
    """
    _platform: Optional[PlatformType]
    _version: Optional[VersionNumberT]
    _is_open: bool
    _has_lock: bool
    _translation_manager: Incomplete
    _bounds: Incomplete
    _changed: bool
    def __init__(self) -> None:
        """
        This must not be used directly. You should instead use :func:`amulet.load_format` or one of the class methods.
        """
    def __del__(self) -> None: ...
    @property
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """
    @property
    @abstractmethod
    def level_name(self) -> str:
        """The name of the level."""
    @property
    def translation_manager(self) -> PyMCTranslate.TranslationManager:
        """The translation manager attached to the world."""
    @translation_manager.setter
    def translation_manager(self, value: PyMCTranslate.TranslationManager): ...
    @staticmethod
    @abstractmethod
    def is_valid(token) -> bool:
        """
        Returns whether this format wrapper is able to load the given data.

        :param token: The token to check. Usually a file or directory path.
        :return: True if the world can be loaded by this format wrapper, False otherwise.
        """
    @staticmethod
    @abstractmethod
    def valid_formats() -> Dict[PlatformType, Tuple[bool, bool]]:
        """
        The valid platform and version combinations that this object can accept.

        This is used when setting the platform and version in the create method
        to verify that the platform and version are valid.

        :return: A dictionary mapping the platform to a tuple of two booleans to determine if numerical and blockstate are valid respectively.
        """
    @property
    def platform(self) -> PlatformType:
        '''Platform string the data is stored in (eg "bedrock" / "java" / ...)'''
    @property
    def version(self) -> VersionNumberT:
        """The version number for the given platform the data is stored in eg (1, 16, 2)"""
    @property
    def max_world_version(self) -> Tuple[PlatformType, VersionNumberT]:
        """
        The version the level was last opened in.

        This should be greater than or equal to the chunk versions found within.
        """
    @property
    def changed(self) -> bool:
        """Has any data been pushed to the format wrapper that has not been saved to disk."""
    @property
    @abstractmethod
    def dimensions(self) -> List[Dimension]:
        """A list of all the dimensions contained in the level."""
    @property
    @abstractmethod
    def can_add_dimension(self) -> bool:
        """
        Can external code register a new dimension.

        If False :meth:`register_dimension` will have no effect.
        """
    @abstractmethod
    def register_dimension(self, dimension_identifier: Any):
        """
        Register a new dimension.

        :param dimension_identifier: The identifier for the dimension.
        """
    @staticmethod
    def requires_selection() -> bool:
        """Does this object require that a selection be defined when creating it from scratch?"""
    @property
    def multi_selection(self) -> bool:
        """
        Does this object support having multiple selection boxes.

        If False it will be given exactly 1 selection.

        If True can be given 0 or more.
        """
    @property
    def selection(self) -> SelectionGroup:
        """The area that all chunk data must fit within."""
    def bounds(self, dimension: Dimension) -> SelectionGroup: ...
    @abstractmethod
    def _get_interface(self, raw_chunk_data: Optional[Any] = ...) -> api_wrapper.Interface: ...
    def _get_interface_and_translator(self, raw_chunk_data: Incomplete | None = ...) -> Tuple[api_wrapper.Interface, 'Translator', VersionNumberAny]: ...
    def _clean_selection(self, selection: SelectionGroup) -> SelectionGroup: ...
    def open(self) -> None:
        """Open the database for reading and writing."""
    @abstractmethod
    def _open(self): ...
    @property
    def is_open(self) -> bool:
        """Has the object been opened."""
    @property
    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
    def _verify_has_lock(self) -> None:
        """
        Ensure that the FormatWrapper is open and has a lock on the object.

        :raises:
            ObjectReadWriteError: if the FormatWrapper does not have a lock on the object.
        """
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
    def save(self) -> None:
        """Save the data back to the level."""
    @abstractmethod
    def _save(self): ...
    def close(self) -> None:
        """Close the level."""
    @abstractmethod
    def _close(self): ...
    @abstractmethod
    def unload(self):
        """Unload data stored in the FormatWrapper class"""
    @abstractmethod
    def all_chunk_coords(self, dimension: Dimension) -> Iterable[ChunkCoordinates]:
        """A generator of all chunk coords in the given dimension."""
    @abstractmethod
    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        """
        Does the chunk exist in the world database?

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the chunk from.
        :return: True if the chunk exists. Calling load_chunk on this chunk may still throw ChunkLoadError
        """
    def _safe_load(self, meth: Callable, args: Tuple[Any, ...], msg: str, load_error: Type[EntryLoadError], does_not_exist_error: Type[EntryDoesNotExist]): ...
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
    def _load_chunk(self, cx: int, cz: int, dimension: Dimension, recurse: bool = ...) -> Chunk:
        """
        Loads and creates a universal :class:`~amulet.api.chunk.Chunk` object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the chunk from.
        :param recurse: bool: look in boundary chunks if required to fully define data
        :return: The chunk at the given coordinates.
        """
    @staticmethod
    def _decode(interface: api_wrapper.Interface, dimension: Dimension, cx: int, cz: int, raw_chunk_data: Any) -> Tuple[Chunk, AnyNDArray]: ...
    def _unpack(self, translator: Translator, game_version: VersionNumberAny, chunk: Chunk, block_palette: AnyNDArray) -> Chunk: ...
    def _convert_to_load(self, chunk: Chunk, translator: Translator, game_version: VersionNumberAny, dimension: Dimension, recurse: bool = ...) -> Chunk: ...
    def commit_chunk(self, chunk: Chunk, dimension: Dimension):
        """
        Save a universal format chunk to the FormatWrapper database (not the level database)

        Call save method to write changed chunks back to the level.

        :param chunk: The chunk object to translate and save.
        :param dimension: The dimension to commit the chunk to.
        """
    def _commit_chunk(self, chunk: Chunk, dimension: Dimension, recurse: bool = ...):
        """
        Saves a universal :class:`~amulet.api.chunk.Chunk` object.

        Calls the interface then the translator.

        It then calls _put_chunk_data to store the data returned by the interface
        """
    def _convert_to_save(self, chunk: Chunk, chunk_version: VersionNumberAny, translator: Translator, recurse: bool = ...) -> Chunk:
        """Convert the Chunk in Universal format to a Chunk in the version specific format."""
    def _pack(self, chunk: Chunk, translator: Translator, chunk_version: VersionNumberAny) -> Tuple[Chunk, AnyNDArray]:
        """Pack the chunk data into the format required by the encoder.
        This includes converting the string names to numerical formats for the versions that require it.
        """
    def _encode(self, interface: api_wrapper.Interface, chunk: Chunk, dimension: Dimension, chunk_palette: AnyNDArray) -> Any:
        """Encode the data to the raw format as saved on disk."""
    def delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        """
        Delete the given chunk from the level.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        """
    @abstractmethod
    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension): ...
    def put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        """
        Commit the raw chunk data to the FormatWrapper cache.

        Call :meth:`save` to push all the cache data to the level.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param data: The raw data to commit to the level.
        :param dimension: The dimension to load the data from.
        """
    @abstractmethod
    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension): ...
    def get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
    @abstractmethod
    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
    @abstractmethod
    def all_player_ids(self) -> Iterable[str]:
        """
        Returns a set of all player ids that are present in the level
        """
    @abstractmethod
    def has_player(self, player_id: str) -> bool:
        """
        Test if a player id is present in the level.
        """
    def load_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player should be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
    @abstractmethod
    def _load_player(self, player_id: str) -> Player:
        """
        Get the raw player data and unpack it into a Player class.

        :param player_id: The id of the player to get.
        :return:
        """
    def get_raw_player_data(self, player_id: str) -> Any:
        """
        Get the player data in the lowest level form.

        :param player_id: The id of the player to get.
        :return:
        """
    @abstractmethod
    def _get_raw_player_data(self, player_id: str) -> Any: ...

class CreatableFormatWrapper(ABC, metaclass=abc.ABCMeta):
    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> Union[BaseFormatWrapper, CreatableFormatWrapper]:
        """
        Create a new instance without any existing data.
        If writing data to disk it must write a valid level.
        If only setting attributes, the open method must be aware that it should not load data from disk.
        :return: A new FormatWrapper instance
        """

class LoadableFormatWrapper(ABC, metaclass=abc.ABCMeta):
    @classmethod
    @abstractmethod
    def load(cls, *args, **kwargs) -> Union[BaseFormatWrapper, LoadableFormatWrapper]:
        """
        Create a new instance from existing data.
        :return: A new FormatWrapper instance
        """

_blind_call_init: Incomplete

class StorageType(IntEnum):
    File: int
    Directory: int

class DiskFormatWrapper(BaseFormatWrapper[VersionNumberT], CreatableFormatWrapper, LoadableFormatWrapper, metaclass=abc.ABCMeta):
    """A FormatWrapper for a level with data entirely on the users disk."""
    _path: Incomplete
    def __init__(self, path: str) -> None:
        """
        Construct a new instance of :class:`DiskFormatWrapper`.

        This must not be used directly. You should instead use :func:`amulet.load_format` or one of the class methods.

        :param path: The file path to the serialised data.
        """
    @property
    def path(self) -> str:
        """The path to the data on disk."""
    _platform: Incomplete
    _version: Incomplete
    @classmethod
    def create(cls, *, path: str, platform: PlatformType, version: VersionNumberAny, bounds: Union[SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None] = ..., overwrite: bool = ..., **kwargs) -> DiskFormatWrapper:
        """
        Create a new instance without any existing data.
        If writing data to disk it must write a valid level.
        If only setting attributes, the open method must be aware that it should not load data from disk.
        :param path:
        :param platform: The platform the data should use.
        :param version: The version the data should use.
        :param bounds: The bounds for each dimension. If one :class:`SelectionGroup` is given it will be applied to all dimensions.
        :param overwrite: Should an existing database be overwritten. If this is False and one exists and error will be thrown.
        :param kwargs: Extra arguments as each implementation requires.
        :return: A new FormatWrapper instance
        """
    @abstractmethod
    def _create(self, overwrite: bool, bounds: Union[SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None] = ..., **kwargs):
        """Set up the database from scratch."""
    @classmethod
    def load(cls, path: str) -> DiskFormatWrapper:
        """
        Create a new instance from existing data.
        :return: A new FormatWrapper instance
        """
    @abstractmethod
    def _shallow_load(self):
        """
        Load minimal data from disk.
        The level may be open somewhere else.
        This code must not cause issues if it is already open.
        """
    @staticmethod
    @abstractmethod
    def storage_type() -> StorageType: ...
    @property
    def exists(self) -> bool:
        """Does some data exist at the specified path."""
FormatWrapper = DiskFormatWrapper

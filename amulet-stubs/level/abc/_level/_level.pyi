import abc
from PIL import Image
from PyMCTranslate import TranslationManager as TranslationManager
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amulet import IMG_DIRECTORY as IMG_DIRECTORY
from amulet.api.data_types import DimensionID as DimensionID, PlatformType as PlatformType
from amulet.chunk import Chunk as Chunk
from amulet.level.abc._dimension import Dimension as Dimension
from amulet.level.abc._history import HistoryManager as HistoryManager
from amulet.level.abc._player_storage import PlayerStorage as PlayerStorage
from amulet.level.abc._raw_level import RawLevel as RawLevel
from amulet.utils.shareable_lock import ShareableRLock as ShareableRLock
from amulet.utils.signal import Signal as Signal, SignalInstanceCacheName as SignalInstanceCacheName
from amulet.version import AbstractVersion as AbstractVersion
from contextlib import AbstractContextManager as ContextManager
from runtime_final import final as final
from typing import Callable, Generic, Iterator, Optional, Type, TypeVar

log: Incomplete
missing_world_icon_path: Incomplete
missing_world_icon: Optional[Image.Image]
LevelPrivateT = TypeVar('LevelPrivateT', bound='LevelPrivate')
LevelT = TypeVar('LevelT', bound='Level')
RawLevelT = TypeVar('RawLevelT', bound='RawLevel')

class LevelPrivate(Generic[LevelT]):
    """Private data and methods that friends of BaseLevel can use."""
    _level: Callable[[], Optional[LevelT]]
    _history_manager: Optional[HistoryManager]
    __slots__: Incomplete
    opened: Incomplete
    closed: Incomplete
    def __init__(self, level: LevelT) -> None: ...
    @property
    def level(self) -> LevelT:
        """
        Get the level that owns this private data.
        If the level instance no longer exists, this will raise RuntimeError.
        """
    def open(self) -> None: ...
    def _open(self) -> None: ...
    def close(self) -> None: ...
    def _close(self) -> None: ...
    @property
    def history_manager(self) -> HistoryManager: ...

class LevelFriend(Generic[LevelPrivateT]):
    _l: LevelPrivateT
    __slots__: Incomplete
    def __init__(self, level_data: LevelPrivateT) -> None: ...

class Level(LevelFriend[LevelPrivateT], ABC, Generic[LevelPrivateT, RawLevelT], metaclass=abc.ABCMeta):
    """Base class for all levels."""
    _level_lock: ShareableRLock
    _is_open: bool
    _history_enabled: bool
    _translator: TranslationManager
    __slots__: Incomplete
    def __init__(self) -> None:
        """
        This cannot be called directly.
        You must use one of the constructor classmethods
        """
    @abstractmethod
    def _instance_data(self) -> LevelPrivateT: ...
    def __del__(self) -> None: ...
    opened: Incomplete
    def open(self) -> None:
        """
        Open the level.
        If the level is already open, this does nothing.
        """
    @abstractmethod
    def _open(self) -> None: ...
    @property
    def is_open(self) -> bool:
        """Has the level been opened"""
    changed: Incomplete
    external_changed: Incomplete
    @abstractmethod
    def save(self) -> None: ...
    purged: Incomplete
    def purge(self) -> None:
        """
        Unload all loaded data.
        This is a nuclear function and must be used with :meth:`lock`

        This is functionally the same as closing and reopening the level.
        """
    closed: Incomplete
    def close(self) -> None:
        """
        Close the level.
        If the level is not open, this does nothing.
        """
    @abstractmethod
    def _close(self) -> None: ...
    @property
    @abstractmethod
    def platform(self) -> PlatformType: ...
    @property
    @abstractmethod
    def max_game_version(self) -> AbstractVersion: ...
    history_changed: Incomplete
    @property
    def undo_count(self) -> int: ...
    def undo(self) -> None: ...
    @property
    def redo_count(self) -> int: ...
    def redo(self) -> None: ...
    def _lock(self, *, edit: bool, parallel: bool, blocking: bool, timeout: float) -> Iterator[None]: ...
    def lock_unique(self, *, blocking: bool = ..., timeout: float = ...) -> ContextManager[None]:
        """
        Get exclusive access to the level without editing it.
        If you want to edit the level with exclusive access, use :meth:`edit_serial` instead.
        If the level is being used by other threads, this will block until they are done.
        Once acquired it will block other threads from accessing the level until this is released.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :return:
        """
    def lock_shared(self, *, blocking: bool = ..., timeout: float = ...) -> ContextManager[None]:
        """
        Share the level without editing it.
        If you want to edit the level in parallel with other threads, use :meth:`edit_parallel` instead.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :return:
        """
    def edit_serial(self, *, blocking: bool = ..., timeout: float = ...) -> ContextManager[None]:
        """
        Get exclusive editing permissions for this level.
        This is useful if you are doing something nuclear to the level and you don't want other code editing it at
        the same time. Usually :meth:`edit_parallel` is sufficient when used with other locks.

        >>> level: Level
        >>> with level.edit_serial():  # This will block the thread until all other threads have finished with the level
        >>>     # any code here will be run without any other threads touching the level
        >>> # Other threads can modify the level here

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :return:
        """
    def edit_parallel(self, *, blocking: bool = ..., timeout: float = ...) -> ContextManager[None]:
        """
        Edit the level in parallal with other threads.
        This allows multiple threads that don't make nuclear changes to work in parallel.
        Before modifying the level data, you must use this or :meth:`edit_serial`.
        Using this ensures that no nuclear changes are made by other threads while your code is running.
        If another thread has exclusive access to the level, this will block until it has finished and vice versa.
        If you are going to make any nuclear changes to the level you must use :meth:`edit_serial` instead.

        >>> level: Level
        >>> with level.edit_parallel():  # This will block the thread until all other threads have finished with the level
        >>>     # any code here will be run without any other threads touching the level
        >>> # Other threads can modify the level here

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :return:
        """
    history_enabled_changed: Incomplete
    @property
    def history_enabled(self) -> bool:
        """Should edit_serial and edit_parallel create undo points and should setting data load the original state."""
    @history_enabled.setter
    def history_enabled(self, history_enabled: bool) -> None: ...
    @property
    def thumbnail(self) -> Image.Image: ...
    @property
    @abstractmethod
    def level_name(self) -> str:
        """The human-readable name of the level"""
    @property
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """
    @property
    def translator(self) -> TranslationManager: ...
    @abstractmethod
    def dimensions(self) -> frozenset[DimensionID]: ...
    @abstractmethod
    def get_dimension(self, dimension: DimensionID) -> Dimension: ...
    @property
    @abstractmethod
    def raw(self) -> RawLevelT:
        """
        Direct access to the level data.
        Only use this if you know what you are doing.
        """
    @property
    @abstractmethod
    def player(self) -> PlayerStorage:
        """Methods to interact with the player data for the level."""
    @property
    @abstractmethod
    def native_chunk_class(self) -> Type[Chunk]: ...

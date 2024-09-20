import abc
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager as ContextManager
from typing import Callable, Generic, TypeVar

from _typeshed import Incomplete
from amulet.chunk import Chunk as Chunk
from amulet.data_types import DimensionId as DimensionId
from amulet.img import missing_world_icon_path as missing_world_icon_path
from amulet.level.abc import Dimension as Dimension
from amulet.level.abc import PlayerStorage as PlayerStorage
from amulet.level.abc import RawLevel as RawLevel
from amulet.level.abc._history import HistoryManager as HistoryManager
from amulet.utils.shareable_lock import ShareableRLock as ShareableRLock
from amulet.utils.signal import Signal as Signal
from amulet.utils.signal import SignalInstanceCacheName as SignalInstanceCacheName
from amulet.utils.task_manager import AbstractCancelManager as AbstractCancelManager
from amulet.utils.task_manager import VoidCancelManager as VoidCancelManager
from amulet.utils.weakref import CallableWeakMethod as CallableWeakMethod
from amulet.version import PlatformType as PlatformType
from amulet.version import VersionNumber as VersionNumber
from PIL import Image
from runtime_final import final as final

log: Incomplete
missing_world_icon: Image.Image | None
RawLevelT = TypeVar("RawLevelT", bound="RawLevel")
DimensionT = TypeVar("DimensionT", bound="Dimension")

class LevelOpenData:
    """Private level attributes that only exist when the level is open."""

    history_manager: HistoryManager
    def __init__(self) -> None: ...

OpenLevelDataT = TypeVar("OpenLevelDataT", bound=LevelOpenData)

class Level(ABC, Generic[OpenLevelDataT, DimensionT, RawLevelT], metaclass=abc.ABCMeta):
    """Base class for all levels."""

    def __init__(self) -> None:
        """
        This cannot be called directly.
        You must use one of the constructor classmethods
        """

    def __del__(self) -> None: ...
    opened: Incomplete
    def open(self, task_manager: AbstractCancelManager = ...) -> None:
        """Open the level.

        If the level is already open, this does nothing.

        :param task_manager: The cancel manager through which cancel can be requested.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """

    def is_open(self, task_manager: AbstractCancelManager = ...) -> bool:
        """Has the level been opened.

        :param task_manager: The cancel manager through which cancel can be requested.
        :return: True if the level is open otherwise False.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """
    changed: Incomplete
    external_changed: Incomplete
    @abstractmethod
    def save(self) -> None: ...
    purged: Incomplete
    def purge(self) -> None:
        """
        Unload all loaded data.
        This is a nuclear function and must be used with :meth:`lock_unique`

        This is functionally the same as closing and reopening the level.
        """
    closing: Incomplete
    closed: Incomplete
    def close(self, task_manager: AbstractCancelManager = ...) -> None:
        """Close the level.

        If the level is not open, this does nothing.

        :param task_manager: The cancel manager through which cancel can be requested.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """

    @property
    @abstractmethod
    def platform(self) -> PlatformType: ...
    @property
    @abstractmethod
    def max_game_version(self) -> VersionNumber: ...
    history_changed: Incomplete
    @property
    def undo_count(self) -> int: ...
    def undo(self) -> None: ...
    @property
    def redo_count(self) -> int: ...
    def redo(self) -> None: ...
    def lock_unique(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = ...
    ) -> ContextManager[None]:
        """
        Get exclusive access to the level without editing it.
        If you want to edit the level with exclusive access, use :meth:`edit_serial` instead.
        If the level is being used by other threads, this will block until they are done.
        Once acquired it will block other threads from accessing the level until this is released.

        >>> level: Level
        >>> with level.lock_unique():
        >>>     # Lock is acquired before entering this block
        >>>     ...
        >>>     # Lock is released before exiting this block

        :param blocking: Should this block until the lock can be acquired. Default is True.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: The cancel manager through which cancel can be requested.
        :return: A context manager to acquire the lock.
        :raises amulet.utils.shareable_lock.LockNotAcquired: If timeout was reached or cancel was called.
        """

    def lock_shared(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = ...
    ) -> ContextManager[None]:
        """
        Share the level without editing it.
        If you want to edit the level in parallel with other threads, use :meth:`edit_parallel` instead.

        >>> level: Level
        >>> with level.lock_shared():
        >>>     # Lock is acquired before entering this block
        >>>     ...
        >>>     # Lock is released before exiting this block

        :param blocking: Should this block until the lock can be acquired. Default is True.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: The cancel manager through which cancel can be requested.
        :return: A context manager to acquire the lock.
        :raises amulet.utils.shareable_lock.LockNotAcquired: If timeout was reached or cancel was called.
        """

    def edit_serial(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = ...
    ) -> ContextManager[None]:
        """
        Get exclusive editing permissions for this level.
        This is useful if you are doing something nuclear to the level and you don't want other code editing it at
        the same time. Usually :meth:`edit_parallel` is sufficient when used with other locks.

        >>> level: Level
        >>> with level.edit_serial():  # This will block the thread until all other threads have finished with the level
        >>>     # Lock is acquired before entering this block
        >>>     # any code here will be run without any other threads touching the level
        >>>     ...
        >>>     # Lock is released before exiting this block
        >>> # Other threads can modify the level here

        :param blocking: Should this block until the lock can be acquired. Default is True.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: The cancel manager through which cancel can be requested.
        :return: A context manager to acquire the lock.
        :raises amulet.utils.shareable_lock.LockNotAcquired: If timeout was reached or cancel was called.
        """

    def edit_parallel(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = ...
    ) -> ContextManager[None]:
        """
        Edit the level in parallal with other threads.
        This allows multiple threads that don't make nuclear changes to work in parallel.
        Before modifying the level data, you must use this or :meth:`edit_serial`.
        Using this ensures that no nuclear changes are made by other threads while your code is running.
        If another thread has exclusive access to the level, this will block until it has finished and vice versa.
        If you are going to make any nuclear changes to the level you must use :meth:`edit_serial` instead.

        >>> level: Level
        >>> with level.edit_serial():  # This will block the thread until all other unique calls have finished with the level
        >>>     # Lock is acquired before entering this block
        >>>     # any code here will be run in parallel with other parallel calls.
        >>>     ...
        >>>     # Lock is released before exiting this block
        >>> # Other threads can modify the level here

        :param blocking: Should this block until the lock can be acquired. Default is True.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :param task_manager: The cancel manager through which cancel can be requested.
        :return: A context manager to acquire the lock.
        :raises amulet.utils.shareable_lock.LockNotAcquired: If timeout was reached or cancel was called.
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
    @abstractmethod
    def modified_time(self) -> float:
        """The unix float timestamp of when the level was last modified."""

    @property
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """

    @abstractmethod
    def dimension_ids(self) -> frozenset[DimensionId]: ...
    @abstractmethod
    def get_dimension(self, dimension_id: DimensionId) -> DimensionT: ...
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
    def native_chunk_class(self) -> type[Chunk]: ...

LevelT = TypeVar("LevelT", bound=Level)

class LevelFriend(Generic[LevelT]):
    """A base class for friends of the level that need to store a pointer to the level"""

    def __init__(self, level_ref: Callable[[], LevelT | None]) -> None: ...

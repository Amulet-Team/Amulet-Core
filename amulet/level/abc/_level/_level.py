from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, TypeVar, Type, Generic, Iterator, Callable
from contextlib import contextmanager, AbstractContextManager as ContextManager
import os
import logging
from weakref import finalize

from runtime_final import final
from PIL import Image

from amulet import IMG_DIRECTORY
from amulet.version import PlatformType, VersionNumber
from amulet.data_types import DimensionId

from amulet.chunk import Chunk

from amulet.utils.shareable_lock import ShareableRLock
from amulet.utils.signal import Signal, SignalInstanceCacheName
from amulet.utils.task_manager import AbstractCancelManager, VoidCancelManager

from amulet.level.abc._history import HistoryManager
from amulet.utils.weakref import CallableWeakMethod


if TYPE_CHECKING:
    from amulet.level.abc import Dimension  # noqa
    from amulet.level.abc import PlayerStorage
    from amulet.level.abc import RawLevel  # noqa

log = logging.getLogger(__name__)

missing_world_icon_path = os.path.abspath(
    os.path.join(IMG_DIRECTORY, "missing_world_icon.png")
)
missing_world_icon: Optional[Image.Image] = None


RawLevelT = TypeVar("RawLevelT", bound="RawLevel")
DimensionT = TypeVar("DimensionT", bound="Dimension")


class LevelOpenData:
    """Private level attributes that only exist when the level is open."""

    history_manager: HistoryManager

    def __init__(self) -> None:
        self.history_manager = HistoryManager()


OpenLevelDataT = TypeVar("OpenLevelDataT", bound=LevelOpenData)


class Level(ABC, Generic[OpenLevelDataT, DimensionT, RawLevelT]):
    """Base class for all levels."""

    __finalise: finalize
    _open_data: OpenLevelDataT | None
    _level_lock: ShareableRLock
    _history_enabled: bool

    __slots__ = (
        "__weakref__",
        "__finalise",
        SignalInstanceCacheName,
        "_open_data",
        "_level_lock",
        "_history_enabled",
    )

    def __init__(self) -> None:
        """
        This cannot be called directly.
        You must use one of the constructor classmethods
        """
        # Private attributes
        self._open_data = None
        self._level_lock = ShareableRLock()
        self._history_enabled = True
        self.__finalise = finalize(self, CallableWeakMethod(self.close))

    def __del__(self) -> None:
        self.__finalise()

    opened = Signal[()]()

    @final
    def open(self, task_manager: AbstractCancelManager = VoidCancelManager()) -> None:
        """Open the level.

        If the level is already open, this does nothing.

        :param task_manager: The cancel manager through which cancel can be requested.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """
        with self.lock_unique(task_manager=task_manager):
            if self.is_open(task_manager=task_manager):
                # Do nothing if already open
                return
            self._open()
            if self._open_data is None:
                raise RuntimeError("_open_data has not been set")
            self._open_data.history_manager.history_changed.connect(
                self.history_changed
            )
            self.opened.emit()

    @abstractmethod
    def _open(self) -> None:
        raise NotImplementedError

    @final
    def is_open(
        self, task_manager: AbstractCancelManager = VoidCancelManager()
    ) -> bool:
        """Has the level been opened.

        :param task_manager: The cancel manager through which cancel can be requested.
        :return: True if the level is open otherwise False.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """
        with self.lock_shared(task_manager=task_manager):
            return self._open_data is not None

    @final
    @property
    def _o(self) -> OpenLevelDataT:
        o = self._open_data
        if o is None:
            raise RuntimeError("Level is not open")
        return o

    # Has the internal state changed
    changed = Signal[()]()
    # Has the external state been changed without our knowledge
    external_changed = Signal[()]()

    @abstractmethod
    def save(self) -> None:
        raise NotImplementedError

    # Signal to notify all listeners that the data they hold is no longer valid
    purged = Signal[()]()

    def purge(self) -> None:
        """
        Unload all loaded data.
        This is a nuclear function and must be used with :meth:`lock_unique`

        This is functionally the same as closing and reopening the level.
        """
        self._o.history_manager.reset()
        self.purged.emit()
        self.history_changed.emit()

    # Signal to notify all listeners that the level has been closed.
    closing = Signal[()]()
    closed = Signal[()]()

    @final
    def close(self, task_manager: AbstractCancelManager = VoidCancelManager()) -> None:
        """Close the level.

        If the level is not open, this does nothing.

        :param task_manager: The cancel manager through which cancel can be requested.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """
        with self.lock_unique(task_manager=task_manager):
            if not self.is_open(task_manager=task_manager):
                # Do nothing if already closed
                return
            self.closing.emit()
            self._close()
            if self._open_data is not None:
                raise RuntimeError("_open_data is still set")
            self.closed.emit()

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def platform(self) -> PlatformType:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_game_version(self) -> VersionNumber:
        raise NotImplementedError

    # Emitted when the undo or redo count has changed
    history_changed = Signal[()]()

    @property
    def undo_count(self) -> int:
        return self._o.history_manager.undo_count

    def undo(self) -> None:
        with self.lock_unique(blocking=False):
            self._o.history_manager.undo()

    @property
    def redo_count(self) -> int:
        return self._o.history_manager.redo_count

    def redo(self) -> None:
        with self.lock_unique(blocking=False):
            self._o.history_manager.redo()

    @contextmanager
    def _lock(
        self,
        *,
        edit: bool,
        parallel: bool,
        blocking: bool,
        timeout: float,
        task_manager: AbstractCancelManager = VoidCancelManager(),
    ) -> Iterator[None]:
        if parallel:
            lock = self._level_lock.shared(blocking, timeout, task_manager)
        else:
            lock = self._level_lock.unique(blocking, timeout, task_manager)
        with lock:
            if edit and self.history_enabled:
                self._o.history_manager.create_undo_bin()
            yield

    def lock_unique(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
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
        return self._lock(
            edit=False,
            parallel=False,
            blocking=blocking,
            timeout=timeout,
            task_manager=task_manager,
        )

    def lock_shared(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
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
        return self._lock(
            edit=False,
            parallel=True,
            blocking=blocking,
            timeout=timeout,
            task_manager=task_manager,
        )

    def edit_serial(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
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
        return self._lock(
            edit=True,
            parallel=False,
            blocking=blocking,
            timeout=timeout,
            task_manager=task_manager,
        )

    def edit_parallel(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
        task_manager: AbstractCancelManager = VoidCancelManager(),
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
        return self._lock(
            edit=True,
            parallel=True,
            blocking=blocking,
            timeout=timeout,
            task_manager=task_manager,
        )

    history_enabled_changed = Signal[()]()

    @property
    def history_enabled(self) -> bool:
        """Should edit_serial and edit_parallel create undo points and should setting data load the original state."""
        return self._history_enabled

    @history_enabled.setter
    def history_enabled(self, history_enabled: bool) -> None:
        self._history_enabled = history_enabled
        self.history_enabled_changed.emit()

    @property
    def thumbnail(self) -> Image.Image:
        global missing_world_icon
        if missing_world_icon is None:
            missing_world_icon = Image.open(missing_world_icon_path)
        return missing_world_icon

    @property
    @abstractmethod
    def level_name(self) -> str:
        """The human-readable name of the level"""
        raise NotImplementedError

    @property
    @abstractmethod
    def modified_time(self) -> float:
        """The unix float timestamp of when the level was last modified."""
        raise NotImplementedError

    @property
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """
        return 16

    @abstractmethod
    def dimension_ids(self) -> frozenset[DimensionId]:
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self, dimension_id: DimensionId) -> DimensionT:
        raise NotImplementedError

    @property
    @abstractmethod
    def raw(self) -> RawLevelT:
        """
        Direct access to the level data.
        Only use this if you know what you are doing.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def player(self) -> PlayerStorage:
        """Methods to interact with the player data for the level."""
        raise NotImplementedError

    @property
    @abstractmethod
    def native_chunk_class(self) -> Type[Chunk]:
        raise NotImplementedError


LevelT = TypeVar("LevelT", bound=Level)


class LevelFriend(Generic[LevelT]):
    """A base class for friends of the level that need to store a pointer to the level"""

    _l_ref: Callable[[], LevelT | None]

    __slots__ = ("_level_ref",)

    def __init__(self, level_ref: Callable[[], LevelT | None]):
        self._l_ref = level_ref

    @property
    def _l(self) -> LevelT:
        level = self._l_ref()
        if level is None:
            raise RuntimeError("The level is no longer accessible")
        return level

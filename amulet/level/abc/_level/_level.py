from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, TypeVar, Callable, Type, Generic, Iterator
from contextlib import contextmanager, AbstractContextManager as ContextManager
import os
import logging
from weakref import ref

from runtime_final import final
from PIL import Image

import PyMCTranslate
from PyMCTranslate import TranslationManager

from amulet import IMG_DIRECTORY
from amulet.version import AbstractVersion
from amulet.api.data_types import DimensionID, PlatformType

from amulet.chunk import Chunk

from amulet.utils.shareable_lock import ShareableRLock
from amulet.utils.signal import Signal, SignalInstanceCacheName

from amulet.level.abc._history import HistoryManager


if TYPE_CHECKING:
    from amulet.level.abc._dimension import Dimension
    from amulet.level.abc._player_storage import PlayerStorage
    from amulet.level.abc._raw_level import RawLevel

log = logging.getLogger(__name__)

missing_world_icon_path = os.path.abspath(
    os.path.join(IMG_DIRECTORY, "missing_world_icon.png")
)
missing_world_icon: Optional[Image.Image] = None


LevelPrivateT = TypeVar("LevelPrivateT", bound="LevelPrivate")
LevelT = TypeVar("LevelT", bound="Level")
RawLevelT = TypeVar("RawLevelT", bound="RawLevel")
DimensionT = TypeVar("DimensionT", bound="Dimension")


class LevelPrivate(Generic[LevelT]):
    """Private data and methods that friends of BaseLevel can use."""

    _level: Callable[[], Optional[LevelT]]
    _history_manager: Optional[HistoryManager]

    __slots__ = (
        "_level",
        "_history_manager",
    )

    opened = Signal()
    closed = Signal()

    def __init__(self, level: LevelT) -> None:
        self._level = ref(level)
        self._history_manager = None

    @final
    @property
    def level(self) -> LevelT:
        """
        Get the level that owns this private data.
        If the level instance no longer exists, this will raise RuntimeError.
        """
        level = self._level()
        if level is None:
            raise RuntimeError("The level no longer exists.")
        return level

    @final
    def open(self) -> None:
        self._open()
        self.opened.emit()

    def _open(self) -> None:
        self._history_manager = HistoryManager()

    @final
    def close(self) -> None:
        self.closed.emit()
        self._close()

    def _close(self) -> None:
        self._history_manager = None

    @property
    def history_manager(self) -> HistoryManager:
        if self._history_manager is None:
            raise RuntimeError("The level is not open.")
        return self._history_manager


class LevelFriend(Generic[LevelPrivateT]):
    _l: LevelPrivateT

    __slots__ = ("_l",)

    def __init__(self, level_data: LevelPrivateT) -> None:
        self._l = level_data


class Level(LevelFriend[LevelPrivateT], Generic[LevelPrivateT, DimensionT, RawLevelT], ABC):
    """Base class for all levels."""

    _level_lock: ShareableRLock
    _is_open: bool
    _history_enabled: bool
    _translator: TranslationManager

    __slots__ = (
        SignalInstanceCacheName,
        "_level_lock",
        "_is_open",
        "_history_enabled",
        "_translator",
    )

    def __init__(self) -> None:
        """
        This cannot be called directly.
        You must use one of the constructor classmethods
        """
        # Private attributes
        self._level_lock = ShareableRLock()
        self._is_open = False
        self._history_enabled = True

        # Private data shared by friends of the class
        super().__init__(self._instance_data())

        self.history_changed.connect(self._l.history_manager.history_changed)

    @abstractmethod
    def _instance_data(self) -> LevelPrivateT:
        raise NotImplementedError

    def __del__(self) -> None:
        self.close()

    opened = Signal()

    @final
    def open(self) -> None:
        """
        Open the level.
        If the level is already open, this does nothing.
        """
        if self.is_open:
            # Do nothing if already open
            return
        self._l.open()
        self._open()
        self._is_open = True
        self.opened.emit()

    @abstractmethod
    def _open(self) -> None:
        raise NotImplementedError

    @final
    @property
    def is_open(self) -> bool:
        """Has the level been opened"""
        return self._is_open

    # Has the internal state changed
    changed = Signal()
    # Has the external state been changed without our knowledge
    external_changed = Signal()

    @abstractmethod
    def save(self) -> None:
        raise NotImplementedError

    # Signal to notify all listeners that the data they hold is no longer valid
    purged = Signal()

    def purge(self) -> None:
        """
        Unload all loaded data.
        This is a nuclear function and must be used with :meth:`lock`

        This is functionally the same as closing and reopening the level.
        """
        self._l.history_manager.reset()
        self.purged.emit()
        self.history_changed.emit()

    # Signal to notify all listeners that the level has been closed.
    closed = Signal()

    @final
    def close(self) -> None:
        """
        Close the level.
        If the level is not open, this does nothing.
        """
        if not self.is_open:
            # Do nothing if already closed
            return
        self._is_open = False
        self.closed.emit()
        try:
            self._close()
        finally:
            self._l.close()

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def platform(self) -> PlatformType:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_game_version(self) -> AbstractVersion:
        raise NotImplementedError

    # Emitted when the undo or redo count has changed
    history_changed = Signal()

    @property
    def undo_count(self) -> int:
        return self._l.history_manager.undo_count

    def undo(self) -> None:
        self._l.history_manager.undo()

    @property
    def redo_count(self) -> int:
        return self._l.history_manager.redo_count

    def redo(self) -> None:
        self._l.history_manager.redo()

    @contextmanager
    def _lock(self, *, edit: bool, parallel: bool, blocking: bool, timeout: float) -> Iterator[None]:
        if parallel:
            lock = self._level_lock.shared(blocking, timeout)
        else:
            lock = self._level_lock.unique(blocking, timeout)
        with lock:
            if edit and self.history_enabled:
                self._l.history_manager.create_undo_bin()
            yield

    def lock_unique(
        self, *, blocking: bool = True, timeout: float = -1
    ) -> ContextManager[None]:
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
        return self._lock(
            edit=False, parallel=False, blocking=blocking, timeout=timeout
        )

    def lock_shared(
        self, *, blocking: bool = True, timeout: float = -1
    ) -> ContextManager[None]:
        """
        Share the level without editing it.
        If you want to edit the level in parallel with other threads, use :meth:`edit_parallel` instead.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :return:
        """
        return self._lock(edit=False, parallel=True, blocking=blocking, timeout=timeout)

    def edit_serial(
        self, *, blocking: bool = True, timeout: float = -1
    ) -> ContextManager[None]:
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
        return self._lock(edit=True, parallel=False, blocking=blocking, timeout=timeout)

    def edit_parallel(
        self, *, blocking: bool = True, timeout: float = -1
    ) -> ContextManager[None]:
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
        return self._lock(edit=True, parallel=True, blocking=blocking, timeout=timeout)

    history_enabled_changed = Signal()

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
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """
        return 16

    @property
    def translator(self) -> TranslationManager:
        if self._translator is None:
            self._translator = PyMCTranslate.new_translation_manager()
        return self._translator

    @abstractmethod
    def dimensions(self) -> frozenset[DimensionID]:
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self, dimension: DimensionID) -> DimensionT:
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

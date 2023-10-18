from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Sequence, TypeVar, Callable
from contextlib import contextmanager, AbstractContextManager as ContextManager
import os
import logging
from weakref import ref

from runtime_final import final
from PIL import Image

from PyMCTranslate import TranslationManager

from amulet import IMG_DIRECTORY
from amulet.api.data_types import DimensionID

from amulet.api.registry import BlockManager, BiomeManager

from amulet.utils.shareable_lock import ShareableRLock
from amulet.utils.signal import Signal, SignalInstanceCacheName

from .._history import HistoryManager


if TYPE_CHECKING:
    from .._dimension import Dimension
    from .._player_storage import PlayerStorage
    from .._raw_level import RawLevel

T = TypeVar("T")

log = logging.getLogger(__name__)

missing_world_icon_path = os.path.abspath(
    os.path.join(IMG_DIRECTORY, "missing_world_icon.png")
)
missing_world_icon: Optional[Image.Image] = None


def metadata(f: T) -> T:
    """Data about a level that can be accessed without opening the level."""
    return f


LevelT = TypeVar("LevelT")


class BaseLevelPrivate:
    """Private data and methods that friends of BaseLevel can use."""

    _level: Callable[[], Optional[BaseLevel]]
    history_manager: Optional[HistoryManager]
    block_palette: Optional[BlockManager]
    biome_palette: Optional[BiomeManager]

    __slots__ = tuple(__annotations__)

    opened = Signal()
    closed = Signal()

    def __init__(self, level: BaseLevel):
        self._level = ref(level)
        self.history_manager = None
        self.block_palette = None
        self.biome_palette = None

    @final
    @property
    def level(self) -> BaseLevel:
        """
        Get the level that owns this private data.
        If the level instance no longer exists, this will raise RuntimeError.
        """
        level = self._level()
        if level is None:
            raise RuntimeError("The level no longer exists.")
        return level

    @final
    def open(self):
        self._open()
        self.opened.emit()

    def _open(self):
        self.history_manager = HistoryManager()
        self.block_palette = BlockManager()
        self.biome_palette = BiomeManager()

    @final
    def close(self):
        self.closed.emit()
        self._close()

    def _close(self):
        self.history_manager = None
        self.block_palette = None
        self.biome_palette = None


class BaseLevel(ABC):
    """Base class for all levels."""

    _l: BaseLevelPrivate
    _level_lock: ShareableRLock
    _is_open: bool
    _history_enabled: bool

    __slots__ = (SignalInstanceCacheName,) + tuple(__annotations__)

    def __init__(self):
        """
        This cannot be called directly.
        You must use one of the constructor classmethods
        """
        # Private attributes
        self._level_lock = ShareableRLock()
        self._is_open = False
        self._history_enabled = True

        # Private data shared by friends of the class
        self._l = self._instance_data()

        self.history_changed.connect(self._l.history_manager.history_changed)

    def _instance_data(self) -> BaseLevelPrivate:
        return BaseLevelPrivate(self)

    def __del__(self):
        self.close()

    opened = Signal()

    @final
    def open(self):
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
    def _open(self):
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
    def save(self):
        raise NotImplementedError

    # Signal to notify all listeners that the data they hold is no longer valid
    purged = Signal()

    def purge(self):
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
    def close(self):
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
    def _close(self):
        raise NotImplementedError

    # Emitted when the undo or redo count has changed
    history_changed = Signal()

    @property
    def undo_count(self) -> int:
        return self._l.history_manager.undo_count

    def undo(self):
        self._l.history_manager.undo()

    @property
    def redo_count(self) -> int:
        return self._l.history_manager.redo_count

    def redo(self):
        self._l.history_manager.redo()

    @contextmanager
    def _lock(self, *, edit: bool, parallel: bool, blocking: bool, timeout: float):
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

        >>> level: BaseLevel
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

        >>> level: BaseLevel
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
    def history_enabled(self, history_enabled: bool):
        self._history_enabled = history_enabled
        self.history_enabled_changed.emit()

    @metadata
    @property
    def thumbnail(self) -> Image.Image:
        global missing_world_icon
        if missing_world_icon is None:
            missing_world_icon = Image.open(missing_world_icon_path)
        return missing_world_icon

    @metadata
    @property
    @abstractmethod
    def level_name(self) -> str:
        """The human-readable name of the level"""
        raise NotImplementedError

    @metadata
    @property
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """
        return 16

    @property
    def translator(self) -> TranslationManager:
        raise NotImplementedError

    @abstractmethod
    def dimensions(self) -> frozenset[DimensionID]:
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self, dimension: DimensionID) -> Dimension:
        raise NotImplementedError

    @property
    def block_palette(self) -> BlockManager:
        """The block look up table for this level."""
        block_palette = self._l.block_palette
        if block_palette is None:
            raise RuntimeError("block_palette does not exist. Did you open the level?")
        return block_palette

    @property
    def biome_palette(self) -> BiomeManager:
        """The biome look up table for this level."""
        biome_palette = self._l.biome_palette
        if biome_palette is None:
            raise RuntimeError("biome_palette does not exist. Did you open the level?")
        return biome_palette

    @property
    @abstractmethod
    def raw(self) -> RawLevel:
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

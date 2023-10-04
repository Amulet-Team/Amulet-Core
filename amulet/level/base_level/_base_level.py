from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
)
from contextlib import contextmanager
from runtime_final import final

from amulet.utils.shareable_lock import ShareableRLock
from amulet.utils.signal import Signal


if TYPE_CHECKING:
    from ._base_level_namespaces.chunk import ChunkNamespace
    from ._base_level_namespaces.metadata import MetadataNamespace
    from ._base_level_namespaces.player import PlayerNamespace
    from ._base_level_namespaces.raw import RawNamespace
    from ._base_level_namespaces.readonly_metadata import ReadonlyMetadataNamespace


NativeChunk = Any


class BaseLevelPrivate:
    """Private data and methods that friends of BaseLevel can use."""

    def __init__(self):
        pass
        # History system will go here


class BaseLevel(ABC):
    """Base class for all levels."""

    _data: BaseLevelPrivate

    def __init__(self):
        """
        This cannot be called directly.
        You must use one of the constructor classmethods
        """
        # Private attributes
        self._level_lock = ShareableRLock()
        self._is_open = False
        # self._translation_manager = None
        # self._platform = None
        # self._version = None
        # self._bounds: dict[Dimension, SelectionGroup] = {}
        # self._changed: bool = False

        # Private data shared by friends of the class
        self._data = self._instance_data()

    @staticmethod
    def _instance_data() -> BaseLevelPrivate:
        return BaseLevelPrivate()

    def __del__(self):
        self.close()

    @final
    def open(self):
        """
        Open the level.
        If the level is already open, this does nothing.
        """
        if self.is_open:
            # Do nothing if already open
            return
        self._open()
        self._is_open = True
        self.opened.emit()

    @abstractmethod
    def _open(self):
        raise NotImplementedError

    opened = Signal()

    @property
    def is_open(self) -> bool:
        """Has the level been opened"""
        return self._is_open

    changed = Signal()

    def save(self):
        raise NotImplementedError

    @final
    def close(self):
        """
        Close the level.
        If the level is not open, this does nothing.
        """
        if not self.is_open:
            # Do nothing if already closed
            return
        self._close()
        self._is_open = False
        self.closed.emit()

    @abstractmethod
    def _close(self):
        raise NotImplementedError

    closed = Signal()

    def undo(self):
        raise NotImplementedError

    def redo(self):
        raise NotImplementedError

    @contextmanager
    def lock(self):
        pass

    @contextmanager
    def lock_shared(self):
        pass

    @contextmanager
    def edit_parallel(self, blocking: bool = True, timeout: float = -1):
        """
        Edit the level in parallal with other threads.
        This allows multiple threads that don't make nuclear changes to work in parallel.
        Before touching the level data, you must use this or :meth:`edit_serial`.
        Using this ensures that no nuclear changes are made by other threads while your code is running.
        If another thread is editing the level in serial mode, this will block until it has finished and vice versa.
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
        with self._level_lock.shared(blocking, timeout):
            yield

    @contextmanager
    def edit_serial(self, blocking: bool = True, timeout: float = -1):
        """
        Lock access to the level so that only you have access to it.
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
        with self._level_lock.unique(blocking, timeout):
            yield

    @property
    @abstractmethod
    def readonly_metadata(self) -> ReadonlyMetadataNamespace:
        """Data about the level that can be accessed when the level is open or closed."""
        raise NotImplementedError

    @property
    @abstractmethod
    def metadata(self) -> MetadataNamespace:
        """Metadata about the level."""
        raise NotImplementedError

    @property
    @abstractmethod
    def raw(self) -> RawNamespace:
        """
        Direct access to the level data.
        Only use this if you know what you are doing.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def chunk(self) -> ChunkNamespace:
        """Methods to interact with the chunk data for the level."""
        raise NotImplementedError

    @property
    @abstractmethod
    def player(self) -> PlayerNamespace:
        """Methods to interact with the player data for the level."""
        raise NotImplementedError


"""
History/Locking system
Should support:
    parallel editing
    disabling the history system

Editing: (original state gets loaded)
    load
    change
    set
    
Setting: Creating/Deleting a chunk (setting a new state without loading the first state)
    set
    
MCEdit's solution
    History enabled:
        Before running an operation it created a backup of all the chunks in the selection.
        When undoing the changes it just rolled them back.
        This meant that only chunks within the selection could be reverted.
    History disabled:
        No backup
        
Amulet's solution
    History enabled:
        When chunks are first loaded, they are saved to a cache so they can be restored if needed.
        When setting a chunk, if the initial state does not exist, it gets loaded.
    History disabled:
        When chunks are first loaded, they are saved to a cache. This is quicker to load from and allows unloading.
        When setting a chunk, overwrite the latest entry in the history system. Do not load the initial state.
"""

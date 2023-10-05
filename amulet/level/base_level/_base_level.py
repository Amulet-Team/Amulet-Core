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

History Solution
    cache
        A Least Recently Used RAM database
        If the stored data overflows the configured maximum, it gets pushed to the disk database
        Data is stored as bytes to make size checking simpler
    getting data
        if the data exists in the cache, it is loaded from there and returned
        else it is loaded from the level, serialised and stored in the cache and returned
    setting data
        if history is enabled and the initial state does not exist in the cache,
            load it from the level, serialise and store it in the cache
        store data 
"""

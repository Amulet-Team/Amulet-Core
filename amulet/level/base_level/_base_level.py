from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional
from weakref import ref
from contextlib import contextmanager

from amulet.utils.shareable_lock import ShareableRLock
from amulet.utils.signal import Signal
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    ChunkCoordinates,
    Dimension,
    PlatformType,
)
from amulet.api.selection import SelectionGroup, SelectionBox


class LevelNamespace:
    def __init__(self, level: BaseLevel):
        self.__level = ref(level)

    def _get_level(self) -> BaseLevel:
        level = self.__level()
        if level is None:
            raise RuntimeError("The level no longer exists.")
        return level


class MetadataNamespace(LevelNamespace, ABC):
    """
    Read-only metadata about the level.
    Everything here can be used when the level is open or closed.
    """

    @abstractmethod
    def level_name(self) -> str:
        """The human-readable name of the level"""
        raise NotImplementedError

    def bounds(self, dimension: Dimension) -> SelectionGroup:
        """The editable region of the dimension."""
        raise NotImplementedError


class RawNamespace(LevelNamespace):
    pass


class ChunkNamespace(LevelNamespace):
    pass


class PlayerNamespace(LevelNamespace):
    pass


class BaseLevel(ABC):
    """Base class for all levels."""

    def __init__(self):
        self._level_lock = ShareableRLock()
        self._is_open = False
        self._has_lock = False
        self._translation_manager = None
        self._platform = None
        self._version = None
        self._bounds: dict[Dimension, SelectionGroup] = {}
        self._changed: bool = False

    def __del__(self):
        self.close()

    def open(self):
        """
        Open and lock the level.
        If the level is already open this does nothing.
        """
        pass

    opened = Signal()

    def close(self):
        """
        Close and release the level.
        If the level is not open this does nothing.
        """
        pass

    closed = Signal()

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
    def metadata(self) -> MetadataNamespace:
        raise NotImplementedError

    @property
    def raw(self) -> RawNamespace:
        raise NotImplementedError

    @property
    def chunks(self) -> ChunkNamespace:
        raise NotImplementedError

    @property
    def players(self) -> PlayerNamespace:
        raise NotImplementedError

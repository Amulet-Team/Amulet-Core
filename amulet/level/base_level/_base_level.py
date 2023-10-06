from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Sequence
from contextlib import contextmanager
import os
import logging

from runtime_final import final
from PIL import Image

from amulet import IMG_DIRECTORY
from amulet.api.data_types import Dimension, BiomeType
from amulet.api.block import Block
from amulet.api.registry import BlockManager, BiomeManager
from amulet.api.selection import SelectionGroup
from amulet.utils.shareable_lock import ShareableRLock
from amulet.utils.signal import Signal, SignalInstanceCacheName

from PyMCTranslate import TranslationManager


if TYPE_CHECKING:
    from ._namespaces.chunk import ChunkNamespace
    from ._namespaces.player import PlayerNamespace
    from ._namespaces.raw import RawNamespace


log = logging.getLogger(__name__)
NativeChunk = Any

missing_world_icon_path = os.path.abspath(
    os.path.join(IMG_DIRECTORY, "missing_world_icon.png")
)
missing_world_icon: Optional[Image.Image] = None


class BaseLevelPrivate:
    """Private data and methods that friends of BaseLevel can use."""

    __slots__ = ()

    def __init__(self):
        pass
        # History system will go here


class BaseLevel(ABC):
    """Base class for all levels."""

    __slots__ = (
        SignalInstanceCacheName,
        "_d",
        "_level_lock",
        "_is_open",
    )

    _d: BaseLevelPrivate

    def __init__(self):
        """
        This cannot be called directly.
        You must use one of the constructor classmethods
        """
        # Private attributes
        self._level_lock = ShareableRLock()
        self._is_open = False

        # Private data shared by friends of the class
        self._d = self._instance_data()

    @staticmethod
    def _instance_data() -> BaseLevelPrivate:
        return BaseLevelPrivate()

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
        self._open()
        self._is_open = True
        self.opened.emit()

    @abstractmethod
    def _open(self):
        raise NotImplementedError

    @property
    def is_open(self) -> bool:
        """Has the level been opened"""
        return self._is_open

    # Has the internal state changed
    changed = Signal()
    # Has the external state been changed without our knowledge
    external_changed = Signal()

    def save(self):
        raise NotImplementedError

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
        try:
            self._close()
        except Exception as e:
            raise e
        finally:
            self._is_open = False
            self.closed.emit()

    @abstractmethod
    def _close(self):
        raise NotImplementedError

    @property
    def thumbnail(self) -> Image.Image:
        global missing_world_icon
        if missing_world_icon is None:
            missing_world_icon = Image.open(missing_world_icon_path)
        return missing_world_icon

    @property
    def translator(self) -> TranslationManager:
        raise NotImplementedError

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

    @abstractmethod
    def dimensions(self) -> Sequence[Dimension]:
        raise NotImplementedError

    @abstractmethod
    def bounds(self, dimension: Dimension) -> SelectionGroup:
        """The editable region of the dimension."""
        raise NotImplementedError

    @abstractmethod
    def default_block(self, dimension: Dimension) -> Block:
        """The default block for this dimension"""
        raise NotImplementedError

    @property
    @abstractmethod
    def block_palette(self) -> BlockManager:
        """The block look up table for this level."""
        raise NotImplementedError

    @abstractmethod
    def default_biome(self, dimension: Dimension) -> BiomeType:
        """The default biome for this dimension"""
        raise NotImplementedError

    @property
    @abstractmethod
    def biome_palette(self) -> BiomeManager:
        """The biome look up table for this level."""
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

    def undo(self):
        raise NotImplementedError

    def redo(self):
        raise NotImplementedError

    @contextmanager
    def lock_shared(self, *, blocking: bool = True, timeout: float = -1):
        """
        Share the level without editing it.
        If you want to edit the level in parallel with other threads, use :meth:`edit_parallel` instead.

        :param blocking: Should this block until the lock can be acquired. Default is True.
            If false and the lock cannot be acquired on the first try, this returns False.
        :param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.
        :return:
        """
        with self._level_lock.shared(blocking, timeout):
            yield

    @contextmanager
    def lock(self, *, blocking: bool = True, timeout: float = -1):
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
        with self._level_lock.unique(blocking, timeout):
            yield

    @contextmanager
    def edit_parallel(self, *, blocking: bool = True, timeout: float = -1):
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
        with self._level_lock.shared(blocking, timeout):
            # TODO: history
            yield

    @contextmanager
    def edit_serial(self, *, blocking: bool = True, timeout: float = -1):
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
        with self._level_lock.unique(blocking, timeout):
            # TODO: history
            yield


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

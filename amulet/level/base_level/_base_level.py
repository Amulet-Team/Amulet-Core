from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional, Generator, Any, TypeVar, Generic, Sequence
from weakref import ref
from contextlib import contextmanager
from threading import RLock
from copy import deepcopy
from runtime_final import final

from amulet.utils.shareable_lock import ShareableRLock, LockError
from amulet.utils.signal import Signal
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    ChunkCoordinates,
    Dimension,
    PlatformType,
    BiomeType,
)
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.chunk import Chunk
from amulet.api.block import Block
from amulet.api.registry import BlockManager, BiomeManager
from ._key_lock import KeyLock


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


LevelT = TypeVar("LevelT", bound=BaseLevel)
LevelDataT = TypeVar("LevelDataT", bound=BaseLevelPrivate)


class LevelNamespace(Generic[LevelT]):
    @final
    def __init__(self, level: LevelT, data: LevelDataT):
        self._level_ref = ref(level)
        self._data = data
        self._init()

    def _init(self):
        """Initialise instance attributes"""
        pass

    def _get_level(self) -> LevelT:
        level = self._level_ref()
        if level is None:
            raise RuntimeError("The level no longer exists.")
        return level


class ReadonlyMetadataNamespace(LevelNamespace, ABC):
    """
    Read-only metadata about the level.
    Everything here can be used when the level is open or closed.
    """

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


class MetadataNamespace(LevelNamespace, ABC):
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
        raise NotImplementedError

    @abstractmethod
    def default_biome(self, dimension: Dimension) -> BiomeType:
        """The default biome for this dimension"""
        raise NotImplementedError

    @property
    @abstractmethod
    def biome_palette(self) -> BiomeManager:
        raise NotImplementedError


class RawNamespace(LevelNamespace):
    pass


class ChunkNamespace(LevelNamespace):
    def _init(self):
        self._locks = KeyLock[tuple[str, int, int]]()

    @contextmanager
    def lock(
        self,
        dimension: str,
        cx: int,
        cz: int,
        *,
        blocking: bool = True,
        timeout: float = -1,
    ) -> Generator[None, None, None]:
        """
        Lock access to the chunk.

        >>> level: BaseLevel
        >>> with level.chunk.lock(dimension, cx, cz):
        >>>     # Do what you need to with the chunk
        >>>     # No other threads are able to edit or set the chunk while in this with block.

        If you want to lock, get and set the chunk data :meth:`edit` is probably a better fit.

        :param dimension: The dimension the chunk is stored in.
        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :param blocking: Should this block until the lock is acquired.
        :param timeout: The amount of time to wait for the lock.
        :raises:
            LockNotAcquired: If the lock was not acquired.
        """
        lock = self._locks.get((dimension, cx, cz))
        if not lock.acquire(blocking, timeout):
            # Thread was not acquired
            raise LockError("Lock was not acquired.")
        try:
            yield
        finally:
            lock.release()

    @contextmanager
    def edit(
        self,
        dimension: str,
        cx: int,
        cz: int,
        *,
        blocking: bool = True,
        timeout: float = -1,
    ) -> Generator[Optional[Chunk], None, None]:
        """
        Lock and edit a chunk.

        >>> level: BaseLevel
        >>> with level.chunk.edit(dimension, cx, cz) as chunk:
        >>>     # Edit the chunk data
        >>>     # No other threads are able to edit the chunk while in this with block.
        >>>     # When the with block exits the edited chunk will be automatically set if no exception occurred.
        """
        lock = self._locks.get((dimension, cx, cz))
        if lock.acquire(blocking, timeout):
            chunk = self.get(dimension, cx, cz)
            yield chunk
            # If an exception occurs in user code, this line won't be run.
            self.set(dimension, cx, cz, chunk)
        else:
            yield None

    def coords(self, dimension: Dimension) -> set[tuple[int, int]]:
        """
        The coordinates of every chunk in this dimension of the level.

        This is the combination of chunks saved to the level and chunks yet to be saved.
        """
        raise NotImplementedError

    def has(self, dimension: Dimension, cx: int, cz: int) -> bool:
        """
        Does the chunk exist. This is a quick way to check if the chunk exists without loading it.

        :param dimension: The dimension to load the chunk from.
        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: True if the chunk exists. Calling get_chunk on this chunk may still throw ChunkLoadError
        """
        raise NotImplementedError

    def get(self, dimension: str, cx: int, cz: int) -> Chunk:
        """
        Get a deep copy of the chunk data.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param dimension: The dimension the chunk is stored in.
        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :return: A unique copy of the chunk data.
        """
        raise NotImplementedError

    def set(self, dimension: str, cx: int, cz: int, chunk: Chunk):
        """
        Overwrite the chunk data.
        You must lock access to the chunk before setting it otherwise an exception may be raised.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param dimension: The dimension the chunk is stored in.
        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :param chunk: The chunk data to set.
        :raises:
            LockError: If the chunk is already locked by another thread.
        """
        lock = self._locks.get((dimension, cx, cz))
        if lock.acquire(False):
            try:
                chunk = deepcopy(chunk)
                # TODO set the chunk and notify listeners
            finally:
                lock.release()
        else:
            raise LockError("Cannot set a chunk if it is locked by another thread.")

    def delete(self, dimension: Dimension, cx: int, cz: int):
        """
        Delete a chunk from the level.

        :param dimension: The dimension to delete the chunk from.
        :param cx: The X coordinate of the chunk
        :param cz: The Z coordinate of the chunk
        """
        raise NotImplementedError

    # def on_change(self, callback):
    #     """A notification system for chunk changes."""
    #     raise NotImplementedError

    # @contextmanager
    # def edit_native(
    #     self,
    #     dimension: str,
    #     cx: int,
    #     cz: int,
    #     *,
    #     blocking: bool = True,
    #     timeout: float = -1,
    # ) -> Generator[Optional[NativeChunk], None, None]:
    #     """
    #     Lock and edit a chunk.
    #
    #     >>> level: BaseLevel
    #     >>> with level.chunk.edit_native(dimension, cx, cz) as chunk:
    #     >>>     # Edit the chunk data
    #     >>>     # No other threads are able to edit the chunk while in this with block.
    #     >>>     # When the with block exits the edited chunk will be automatically set if no exception occurred.
    #     """
    #     lock = self._locks.get((dimension, cx, cz))
    #     if lock.acquire(blocking, timeout):
    #         chunk = self.get_native(dimension, cx, cz)
    #         yield chunk
    #         # If an exception occurs in user code, this line won't be run.
    #         self.set_native(dimension, cx, cz, chunk)
    #     else:
    #         yield None
    #
    # def get_native(self, dimension: str, cx: int, cz: int) -> NativeChunk:
    #     raise NotImplementedError
    #
    # def set_native(self, dimension: str, cx: int, cz: int, native_chunk: NativeChunk):
    #     raise NotImplementedError


class PlayerNamespace(LevelNamespace):
    pass

from __future__ import annotations

import pickle
from typing import Optional, Generator, TYPE_CHECKING, TypeVar, Generic
from contextlib import contextmanager
from threading import RLock
from abc import ABC, abstractmethod

from amulet.utils.shareable_lock import LockError
from amulet.chunk import Chunk, ChunkT
from amulet.api.data_types import DimensionID
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError
from amulet.utils.signal import Signal

from ._raw_level import RawDimensionT

from ._level import LevelFriend, LevelPrivateT
from ._history import HistoryManagerLayer


if TYPE_CHECKING:
    from ._level import Level


class ChunkKey(tuple[int, int]):
    def __new__(cls, cx: int, cz: int):
        return super().__new__(cls, (cx, cz))

    def __init__(self, cx: int, cz: int):
        self._bytes: Optional[bytes] = None

    @property
    def cx(self) -> int:
        return self[0]

    @property
    def cz(self) -> int:
        return self[1]

    def __bytes__(self) -> bytes:
        if self._bytes is None:
            self._bytes = b"/".join((str(self[0]).encode(), str(self[1]).encode()))
        return self._bytes


class ChunkHandle(
    LevelFriend[LevelPrivateT],
    Generic[LevelPrivateT, RawDimensionT, ChunkT],
    ABC,
):
    _lock: RLock
    _dimension: DimensionID
    _key: ChunkKey
    _history: HistoryManagerLayer[ChunkKey]
    _raw_dimension: Optional[RawDimensionT]

    __slots__ = tuple(__annotations__)

    def __init__(
        self,
        level_data: LevelPrivateT,
        history: HistoryManagerLayer[ChunkKey],
        dimension: DimensionID,
        cx: int,
        cz: int,
    ):
        super().__init__(level_data)
        self._lock = RLock()
        self._dimension = dimension
        self._key = ChunkKey(cx, cz)
        self._history = history
        self._raw_dimension = None

    changed = Signal()

    @property
    def dimension(self) -> DimensionID:
        return self._dimension

    @property
    def cx(self) -> int:
        return self._key.cx

    @property
    def cz(self) -> int:
        return self._key.cz

    def _get_raw_dimension(self) -> RawDimensionT:
        if self._raw_dimension is None:
            self._raw_dimension = self._l.level.raw.get_dimension(self.dimension)
        return self._raw_dimension

    @contextmanager
    def lock(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
    ) -> Generator[None, None, None]:
        """
        Lock access to the chunk.

        >>> level: Level
        >>> dimension_name: str
        >>> cx: int
        >>> cz: int
        >>> with level.get_dimension(dimension_name).get_chunk_handle(cx, cz).lock():
        >>>     # Do what you need to with the chunk
        >>>     # No other threads are able to edit or set the chunk while in this with block.

        If you want to lock, get and set the chunk data :meth:`edit` is probably a better fit.

        :param blocking: Should this block until the lock is acquired.
        :param timeout: The amount of time to wait for the lock.
        :raises:
            LockNotAcquired: If the lock could not be acquired.
        """
        if not self._lock.acquire(blocking, timeout):
            # Thread was not acquired
            raise LockError("Lock was not acquired.")
        try:
            yield
        finally:
            self._lock.release()

    @contextmanager
    def edit(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
    ) -> Generator[Optional[ChunkT], None, None]:
        """
        Lock and edit a chunk.
        If blocking is false and the lock could not be acquired within the timeout period

        >>> level: Level
        >>> dimension_name: str
        >>> cx: int
        >>> cz: int
        >>> with level.get_dimension(dimension_name).get_chunk_handle(cx, cz).edit() as chunk:
        >>>     # Edit the chunk data
        >>>     # No other threads are able to edit the chunk while in this with block.
        >>>     # When the with block exits the edited chunk will be automatically set if no exception occurred.

        :param blocking: Should this block until the lock is acquired.
        :param timeout: The amount of time to wait for the lock.
        :raises:
            LockNotAcquired: If the lock could not be acquired.
        """
        with self.lock(blocking=blocking, timeout=timeout):
            chunk = self.get()
            yield chunk
            # If an exception occurs in user code, this line won't be run.
            self.set(chunk)

    def exists(self) -> bool:
        """
        Does the chunk exist. This is a quick way to check if the chunk exists without loading it.

        :return: True if the chunk exists. Calling get_chunk on this chunk may still throw ChunkLoadError
        """
        if self._history.has_resource(self._key):
            return self._history.resource_exists(self._key)
        else:
            # The history system is not aware of the chunk. Look in the level data
            return self._get_raw_dimension().has_chunk(self.cx, self.cz)

    def _preload(self):
        if not self._history.has_resource(self._key):
            # The history system is not aware of the chunk. Load from the level data
            try:
                chunk = self._raw_dimension.raw_chunk_to_native_chunk(
                    self.cx,
                    self.cz,
                    self._raw_dimension.get_raw_chunk(self.cx, self.cz),
                )
            except ChunkDoesNotExist:
                data = b""
            except ChunkLoadError as e:
                data = pickle.dumps(e)
            else:
                data = chunk.pickle(self._l.level)

            self._history.set_initial_resource(self._key, data)

    def get(self) -> ChunkT:
        """
        Get a deep copy of the chunk data.
        If you want to edit the chunk, use :meth:`edit` instead.

        :return: A unique copy of the chunk data.
        """
        self._preload()
        data = self._history.get_resource(self._key)
        if data:
            chunk = pickle.loads(data)
            if isinstance(chunk, Chunk):
                return chunk
            elif isinstance(chunk, ChunkLoadError):
                raise chunk
            else:
                raise RuntimeError
        else:
            raise ChunkDoesNotExist

    def _set(self, data: bytes):
        if not self._lock.acquire(False):
            raise LockError("Cannot set a chunk if it is locked by another thread.")
        try:
            history = self._history
            if not history.has_resource(self._key):
                if self._l.level.history_enabled:
                    self._preload()
                else:
                    history.set_initial_resource(self._key, b"")
            history.set_resource(self._key, data)
        finally:
            self._lock.release()
        self.changed.emit()
        self._l.level.changed.emit()

    @abstractmethod
    def _validate_chunk(self, chunk: ChunkT):
        raise NotImplementedError

    def set(self, chunk: ChunkT):
        """
        Overwrite the chunk data.
        You must lock access to the chunk before setting it otherwise an exception may be raised.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        :raises:
            LockError: If the chunk is already locked by another thread.
        """
        self._validate_chunk(chunk)
        self._set(pickle.dumps(chunk))

    def delete(self):
        """Delete the chunk from the level."""
        self._set(b"")


ChunkHandleT = TypeVar("ChunkHandleT", bound=ChunkHandle)

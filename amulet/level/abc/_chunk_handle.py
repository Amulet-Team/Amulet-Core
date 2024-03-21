from __future__ import annotations

import pickle
from typing import Optional, TYPE_CHECKING, Generic, TypeVar, cast
from collections.abc import Iterator
from contextlib import contextmanager
from threading import RLock
from abc import ABC, abstractmethod

from amulet.utils.shareable_lock import LockNotAcquired
from amulet.chunk import Chunk
from amulet.api.data_types import DimensionID
from amulet.errors import ChunkDoesNotExist, ChunkLoadError
from amulet.utils.signal import Signal

from ._level import LevelFriend, LevelT
from ._history import HistoryManagerLayer


if TYPE_CHECKING:
    from ._level import Level
    from ._raw_level import RawDimension


ChunkT = TypeVar("ChunkT", bound=Chunk)
RawDimensionT = TypeVar("RawDimensionT", bound="RawDimension")


class ChunkKey(tuple[int, int]):
    def __new__(cls, cx: int, cz: int) -> ChunkKey:
        return tuple.__new__(cls, (cx, cz))

    def __init__(self, cx: int, cz: int) -> None:
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
    LevelFriend[LevelT],
    ABC,
    Generic[LevelT, RawDimensionT, ChunkT],
):
    _lock: RLock
    _dimension: DimensionID
    _key: ChunkKey
    _history: HistoryManagerLayer[ChunkKey]
    _raw_dimension: Optional[RawDimensionT]

    __slots__ = (
        "_lock",
        "_dimension",
        "_key",
        "_history",
        "_raw_dimension",
    )

    def __init__(
        self,
        level: LevelT,
        history: HistoryManagerLayer[ChunkKey],
        dimension: DimensionID,
        cx: int,
        cz: int,
    ) -> None:
        super().__init__(level)
        self._lock = RLock()
        self._dimension = dimension
        self._key = ChunkKey(cx, cz)
        self._history = history
        self._raw_dimension = None

    changed = Signal[()]()

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
            self._raw_dimension = self._l.raw.get_dimension(self.dimension)
        return self._raw_dimension

    @contextmanager
    def lock(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
    ) -> Iterator[None]:
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
            raise LockNotAcquired("Lock was not acquired.")
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
    ) -> Iterator[Optional[ChunkT]]:
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

    def _preload(self) -> None:
        if not self._history.has_resource(self._key):
            # The history system is not aware of the chunk. Load from the level data
            try:
                chunk = self._get_raw_dimension().raw_chunk_to_native_chunk(
                    self.cx,
                    self.cz,
                    self._get_raw_dimension().get_raw_chunk(self.cx, self.cz),
                )
            except ChunkDoesNotExist:
                data = b""
            except ChunkLoadError as e:
                data = pickle.dumps(e)
            else:
                data = pickle.dumps(chunk)

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
                return cast(ChunkT, chunk)
            elif isinstance(chunk, ChunkLoadError):
                raise chunk
            else:
                raise RuntimeError
        else:
            raise ChunkDoesNotExist

    def _set(self, data: bytes) -> None:
        if not self._lock.acquire(False):
            raise LockNotAcquired(
                "Cannot set a chunk if it is locked by another thread."
            )
        try:
            history = self._history
            if not history.has_resource(self._key):
                if self._l.history_enabled:
                    self._preload()
                else:
                    history.set_initial_resource(self._key, b"")
            history.set_resource(self._key, data)
        finally:
            self._lock.release()
        self.changed.emit()
        self._l.changed.emit()

    @abstractmethod
    def _validate_chunk(self, chunk: ChunkT) -> None:
        raise NotImplementedError

    def set(self, chunk: ChunkT) -> None:
        """
        Overwrite the chunk data.
        You must lock access to the chunk before setting it otherwise an exception may be raised.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        :raises:
            LockNotAcquired: If the chunk is already locked by another thread.
        """
        self._validate_chunk(chunk)
        self._set(pickle.dumps(chunk))

    def delete(self) -> None:
        """Delete the chunk from the level."""
        self._set(b"")

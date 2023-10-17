from __future__ import annotations

from typing import Optional, Generator, TYPE_CHECKING
from contextlib import contextmanager
from threading import RLock

from amulet.utils.shareable_lock import LockError
from amulet.api.chunk import Chunk
from amulet.api.data_types import DimensionID
from amulet.api.errors import ChunkDoesNotExist
from amulet.utils.signal import Signal

from ._level import LevelFriend, BaseLevelPrivate
from ._history import HistoryManagerLayer


if TYPE_CHECKING:
    from ._level import BaseLevel


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


class ChunkHandle(LevelFriend):
    _lock: RLock
    _history: HistoryManagerLayer[ChunkKey]

    __slots__ = tuple(__annotations__)

    def __init__(
        self,
        level_data: BaseLevelPrivate,
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

    changed = Signal()

    @contextmanager
    def lock(
        self,
        *,
        blocking: bool = True,
        timeout: float = -1,
    ) -> Generator[None, None, None]:
        """
        Lock access to the chunk.

        >>> level: BaseLevel
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
    ) -> Generator[Optional[Chunk], None, None]:
        """
        Lock and edit a chunk.
        If blocking is false and the lock could not be acquired within the timeout period

        >>> level: BaseLevel
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
            raise NotImplementedError

    def get(self) -> Chunk:
        """
        Get a deep copy of the chunk data.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :return: A unique copy of the chunk data.
        """
        if self._history.has_resource(self._key):
            data = self._history.get_resource(self._key)
            if data:
                return Chunk.unpickle(data, self._d.level)
            else:
                raise ChunkDoesNotExist
        else:
            # The history system is not aware of the chunk. Load from the level data
            raise NotImplementedError

    def _set(self, data: bytes):
        if not self._lock.acquire(False):
            raise LockError("Cannot set a chunk if it is locked by another thread.")
        try:
            history = self._history
            if not history.has_resource(self._key):
                if self._d.level.history_enabled:
                    raise NotImplementedError
                    # TODO: load the original state
                    # history.set_initial_resource(key)
                else:
                    history.set_initial_resource(self._key, b"")
            history.set_resource(self._key, data)
        finally:
            self._lock.release()
        self.changed.emit()
        self._d.level.changed.emit()

    def set(self, chunk: Chunk):
        """
        Overwrite the chunk data.
        You must lock access to the chunk before setting it otherwise an exception may be raised.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        :raises:
            LockError: If the chunk is already locked by another thread.
        """
        self._set(chunk.pickle(self._d.level))

    def delete(self):
        """Delete the chunk from the level."""
        self._set(b"")

    # @contextmanager
    # def edit_native(
    #     self,
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
    #     >>> with level.chunk.edit_native(cx, cz) as chunk:
    #     >>>     # Edit the chunk data
    #     >>>     # No other threads are able to edit the chunk while in this with block.
    #     >>>     # When the with block exits the edited chunk will be automatically set if no exception occurred.
    #     """
    #     lock = self._locks.get((cx, cz))
    #     if lock.acquire(blocking, timeout):
    #         chunk = self.get_native(cx, cz)
    #         yield chunk
    #         # If an exception occurs in user code, this line won't be run.
    #         self.set_native(cx, cz, chunk)
    #     else:
    #         yield None
    #
    # def get_native(self, cx: int, cz: int) -> NativeChunk:
    #     raise NotImplementedError
    #
    # def set_native(self, cx: int, cz: int, native_chunk: NativeChunk):
    #     raise NotImplementedError

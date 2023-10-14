from __future__ import annotations

from typing import Optional, Generator, TYPE_CHECKING
from contextlib import contextmanager

from amulet.utils.shareable_lock import LockError
from amulet.api.chunk import Chunk
from amulet.api.errors import ChunkDoesNotExist
from amulet.utils.signal import SignalInstance

from ._lock_map import LockMap
from ._level import LevelFriend
from ._history import HistoryManagerLayer
from ._signal_map import SignalMap


if TYPE_CHECKING:
    from ._level import BaseLevel


class ChunkKey(tuple):
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


class ChunkStorage(LevelFriend):
    __slots__ = ("_locks", "_history")

    def _init(self):
        self._locks = LockMap[tuple[int, int]]()
        self._signals = SignalMap[tuple[int, int]]()
        self._history: HistoryManagerLayer[
            ChunkKey
        ] = self._d.history_manager.new_layer()

    @contextmanager
    def lock(
        self,
        cx: int,
        cz: int,
        *,
        blocking: bool = True,
        timeout: float = -1,
    ) -> Generator[None, None, None]:
        """
        Lock access to the chunk.

        >>> level: BaseLevel
        >>> dimension_name: str
        >>> with level.get_dimension(dimension_name).chunk.lock(cx, cz):
        >>>     # Do what you need to with the chunk
        >>>     # No other threads are able to edit or set the chunk while in this with block.

        If you want to lock, get and set the chunk data :meth:`edit` is probably a better fit.

        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :param blocking: Should this block until the lock is acquired.
        :param timeout: The amount of time to wait for the lock.
        :raises:
            LockNotAcquired: If the lock could not be acquired.
        """
        lock = self._locks.get((cx, cz))
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
        cx: int,
        cz: int,
        *,
        blocking: bool = True,
        timeout: float = -1,
    ) -> Generator[Optional[Chunk], None, None]:
        """
        Lock and edit a chunk.
        If blocking is false and the lock could not be acquired within the timeout period

        >>> level: BaseLevel
        >>> dimension_name: str
        >>> with level.get_dimension(dimension_name).chunk.edit(cx, cz) as chunk:
        >>>     # Edit the chunk data
        >>>     # No other threads are able to edit the chunk while in this with block.
        >>>     # When the with block exits the edited chunk will be automatically set if no exception occurred.

        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :param blocking: Should this block until the lock is acquired.
        :param timeout: The amount of time to wait for the lock.
        :raises:
            LockNotAcquired: If the lock could not be acquired.
        """
        with self.lock(cx, cz, blocking=blocking, timeout=timeout):
            chunk = self.get(cx, cz)
            yield chunk
            # If an exception occurs in user code, this line won't be run.
            self.set(cx, cz, chunk)

    def coords(self) -> set[tuple[int, int]]:
        """
        The coordinates of every chunk that exists in this dimension of the level.

        This is the combination of chunks saved to the level and chunks yet to be saved.
        """
        chunks: set[tuple[int, int]] = set()  # TODO: pull the data from the raw level
        for key, state in self._history.resources_exist_map().items():
            if state:
                chunks.add((key.cx, key.cz))
            else:
                chunks.discard((key.cx, key.cz))
        return chunks

    def changed_coords(self) -> set[tuple[int, int]]:
        """The coordinates of every chunk in this level that has been changed since the last save."""
        key: ChunkKey
        return {(key.cx, key.cz) for key in self._history.changed_resources()}

    def has(self, cx: int, cz: int) -> bool:
        """
        Does the chunk exist. This is a quick way to check if the chunk exists without loading it.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: True if the chunk exists. Calling get_chunk on this chunk may still throw ChunkLoadError
        """
        key = ChunkKey(cx, cz)
        if self._history.has_resource(key):
            return self._history.resource_exists(key)
        else:
            # The history system is not aware of the chunk. Look in the level data
            raise NotImplementedError

    def get(self, cx: int, cz: int) -> Chunk:
        """
        Get a deep copy of the chunk data.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :return: A unique copy of the chunk data.
        """
        key = ChunkKey(cx, cz)
        if self._history.has_resource(key):
            data = self._history.get_resource(key)
            if data:
                return Chunk.unpickle(data, self._level)
            else:
                raise ChunkDoesNotExist
        else:
            # The history system is not aware of the chunk. Load from the level data
            raise NotImplementedError

    def _set(self, cx: int, cz: int, data: bytes):
        lock = self._locks.get((cx, cz))
        if not lock.acquire(False):
            raise LockError("Cannot set a chunk if it is locked by another thread.")
        try:
            history = self._history
            key = ChunkKey(cx, cz)
            if not history.has_resource(key):
                if self._level.history_enabled:
                    raise NotImplementedError
                    # TODO: load the original state
                    # history.set_initial_resource(key)
                else:
                    history.set_initial_resource(key, b"")
            history.set_resource(key, data)
        finally:
            lock.release()
        self._signals.emit((cx, cz))

    def set(self, cx: int, cz: int, chunk: Chunk):
        """
        Overwrite the chunk data.
        You must lock access to the chunk before setting it otherwise an exception may be raised.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param cx: The chunk x coordinate.
        :param cz: The chunk z coordinate.
        :param chunk: The chunk data to set.
        :raises:
            LockError: If the chunk is already locked by another thread.
        """
        self._set(cx, cz, chunk.pickle(self._level))

    def delete(self, cx: int, cz: int):
        """
        Delete a chunk from the level.

        :param cx: The X coordinate of the chunk
        :param cz: The Z coordinate of the chunk
        """
        self._set(cx, cz, b"")

    def changed(self, cx: int, cz: int) -> SignalInstance:
        """
        Get a signal instance that is emitted when the chunk data changes.
        The caller must store a strong reference to the returned SignalInstance

        :param cx: The X coordinate of the chunk
        :param cz: The Z coordinate of the chunk
        """
        return self._signals.get((cx, cz))

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

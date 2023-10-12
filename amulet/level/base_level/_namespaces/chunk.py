from __future__ import annotations

from typing import Optional, Generator
from contextlib import contextmanager
from copy import deepcopy

from amulet.utils.shareable_lock import LockError
from amulet.api.data_types import Dimension
from amulet.api.chunk import Chunk
from .._lock_map import LockMap
from .namespace import LevelFriend
from .._level import BaseLevel


    __slots__ = ()
class ChunkNamespace(LevelFriend):

    def _init(self):
        self._locks = LockMap[tuple[int, int]]()

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

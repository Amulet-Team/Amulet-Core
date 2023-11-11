import abc
from ._history import HistoryManagerLayer as HistoryManagerLayer
from ._level import Level as Level, LevelFriend as LevelFriend, LevelPrivateT as LevelPrivateT
from ._raw_level import RawDimension as RawDimension
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amulet.api.data_types import DimensionID as DimensionID
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ChunkLoadError as ChunkLoadError
from amulet.chunk import Chunk as Chunk
from amulet.utils.shareable_lock import LockError as LockError
from amulet.utils.signal import Signal as Signal
from collections.abc import Iterator
from threading import RLock
from typing import Generator, Generic, Optional, TypeVar

ChunkT = TypeVar('ChunkT', bound=Chunk)
RawDimensionT = TypeVar('RawDimensionT', bound='RawDimension')

class ChunkKey(tuple[int, int]):
    def __new__(cls, cx: int, cz: int) -> ChunkKey: ...
    _bytes: Incomplete
    def __init__(self, cx: int, cz: int) -> None: ...
    @property
    def cx(self) -> int: ...
    @property
    def cz(self) -> int: ...
    def __bytes__(self) -> bytes: ...

class ChunkHandle(LevelFriend[LevelPrivateT], ABC, Generic[LevelPrivateT, RawDimensionT, ChunkT], metaclass=abc.ABCMeta):
    _lock: RLock
    _dimension: DimensionID
    _key: ChunkKey
    _history: HistoryManagerLayer[ChunkKey]
    _raw_dimension: Optional[RawDimensionT]
    __slots__: Incomplete
    def __init__(self, level_data: LevelPrivateT, history: HistoryManagerLayer[ChunkKey], dimension: DimensionID, cx: int, cz: int) -> None: ...
    changed: Incomplete
    @property
    def dimension(self) -> DimensionID: ...
    @property
    def cx(self) -> int: ...
    @property
    def cz(self) -> int: ...
    def _get_raw_dimension(self) -> RawDimensionT: ...
    def lock(self, *, blocking: bool = ..., timeout: float = ...) -> Generator[None, None, None]:
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
    def edit(self, *, blocking: bool = ..., timeout: float = ...) -> Iterator[Optional[ChunkT]]:
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
    def exists(self) -> bool:
        """
        Does the chunk exist. This is a quick way to check if the chunk exists without loading it.

        :return: True if the chunk exists. Calling get_chunk on this chunk may still throw ChunkLoadError
        """
    def _preload(self) -> None: ...
    def get(self) -> ChunkT:
        """
        Get a deep copy of the chunk data.
        If you want to edit the chunk, use :meth:`edit` instead.

        :return: A unique copy of the chunk data.
        """
    def _set(self, data: bytes) -> None: ...
    @abstractmethod
    def _validate_chunk(self, chunk: ChunkT) -> None: ...
    def set(self, chunk: ChunkT) -> None:
        """
        Overwrite the chunk data.
        You must lock access to the chunk before setting it otherwise an exception may be raised.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        :raises:
            LockError: If the chunk is already locked by another thread.
        """
    def delete(self) -> None:
        """Delete the chunk from the level."""

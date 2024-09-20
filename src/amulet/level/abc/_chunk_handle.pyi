import abc
from abc import ABC
from collections.abc import Iterable, Iterator
from typing import Callable, Generic, Self, TypeVar

from _typeshed import Incomplete
from amulet.chunk import Chunk as Chunk
from amulet.chunk import get_null_chunk as get_null_chunk
from amulet.data_types import DimensionId as DimensionId
from amulet.errors import ChunkDoesNotExist as ChunkDoesNotExist
from amulet.errors import ChunkLoadError as ChunkLoadError
from amulet.utils.shareable_lock import LockNotAcquired as LockNotAcquired
from amulet.utils.signal import Signal as Signal

from ._history import HistoryManagerLayer as HistoryManagerLayer
from ._level import Level as Level
from ._level import LevelFriend as LevelFriend
from ._level import LevelT as LevelT
from ._raw_level import RawDimension as RawDimension

ChunkT = TypeVar("ChunkT", bound=Chunk)
RawDimensionT = TypeVar("RawDimensionT", bound="RawDimension")

class ChunkKey(tuple[int, int]):
    def __new__(cls, cx: int, cz: int) -> Self: ...
    def __init__(self, cx: int, cz: int) -> None: ...
    @property
    def cx(self) -> int: ...
    @property
    def cz(self) -> int: ...
    def __bytes__(self) -> bytes: ...

class ChunkHandle(
    LevelFriend[LevelT],
    ABC,
    Generic[LevelT, RawDimensionT, ChunkT],
    metaclass=abc.ABCMeta,
):
    """
    A class which manages chunk data.
    You must acquire the lock for the chunk before reading or writing data.
    Some internal synchronisation is done to catch some threading issues.
    """

    def __init__(
        self,
        level_ref: Callable[[], LevelT | None],
        chunk_history: HistoryManagerLayer[ChunkKey],
        chunk_data_history: HistoryManagerLayer[bytes],
        dimension_id: DimensionId,
        cx: int,
        cz: int,
    ) -> None: ...
    changed: Incomplete
    @property
    def dimension_id(self) -> DimensionId: ...
    @property
    def cx(self) -> int: ...
    @property
    def cz(self) -> int: ...
    def lock(self, *, blocking: bool = True, timeout: float = -1) -> Iterator[None]:
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

    def edit(
        self,
        *,
        components: Iterable[str] | None = None,
        blocking: bool = True,
        timeout: float = -1
    ) -> Iterator[ChunkT | None]:
        """Lock and edit a chunk.

        If you only want to access/modify parts of the chunk data you can specify the components you want to load.
        This makes it faster because you don't need to load unneeded parts.

        >>> level: Level
        >>> dimension_name: str
        >>> cx: int
        >>> cz: int
        >>> with level.get_dimension(dimension_name).get_chunk_handle(cx, cz).edit() as chunk:
        >>>     # Edit the chunk data
        >>>     # No other threads are able to edit the chunk while in this with block.
        >>>     # When the with block exits the edited chunk will be automatically set if no exception occurred.

        :param components: None to load all components or an iterable of component strings to load.
        :param blocking: Should this block until the lock is acquired.
        :param timeout: The amount of time to wait for the lock.
        :raises:
            LockNotAcquired: If the lock could not be acquired.
        """

    def exists(self) -> bool:
        """
        Does the chunk exist. This is a quick way to check if the chunk exists without loading it.

        This state may change if the lock is not acquired.

        :return: True if the chunk exists. Calling get on this chunk handle may still throw ChunkLoadError
        """

    def get_class(self) -> type[ChunkT]:
        """Get the chunk class used for this chunk.

        :raises:
            ChunkDoesNotExist if the chunk does not exist.
        """

    def get(self, components: Iterable[str] | None = None) -> ChunkT:
        """Get a unique copy of the chunk data.

        If you want to edit the chunk, use :meth:`edit` instead.

        If you only want to access/modify parts of the chunk data you can specify the components you want to load.
        This makes it faster because you don't need to load unneeded parts.

        :param components: None to load all components or an iterable of component strings to load.
        :return: A unique copy of the chunk data.
        """

    def set(self, chunk: ChunkT) -> None:
        """
        Overwrite the chunk data.
        You must acquire the chunk lock before setting.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        :raises:
            LockNotAcquired: If the chunk is already locked by another thread.
        """

    def delete(self) -> None:
        """Delete the chunk from the level."""

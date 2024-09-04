from __future__ import annotations

import pickle
from typing import Optional, TYPE_CHECKING, Generic, TypeVar, Callable, Self
from collections.abc import Iterator, Iterable
from contextlib import contextmanager
from threading import RLock
from abc import ABC, abstractmethod

from amulet.utils.shareable_lock import LockNotAcquired
from amulet.chunk import Chunk, get_null_chunk
from amulet.data_types import DimensionId
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
    def __new__(cls, cx: int, cz: int) -> Self:
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
    """
    A class which manages chunk data.
    You must acquire the lock for the chunk before reading or writing data.
    Some internal synchronisation is done to catch some threading issues.
    """

    _lock: RLock
    _dimension: DimensionId
    _key: ChunkKey
    _chunk_history: HistoryManagerLayer[ChunkKey]
    _chunk_data_history: HistoryManagerLayer[bytes]
    _raw_dimension: Optional[RawDimensionT]

    __slots__ = (
        "_lock",
        "_dimension_id",
        "_key",
        "_chunk_history",
        "_chunk_data_history",
        "_raw_dimension",
    )

    def __init__(
        self,
        level_ref: Callable[[], LevelT | None],
        chunk_history: HistoryManagerLayer[ChunkKey],
        chunk_data_history: HistoryManagerLayer[bytes],
        dimension_id: DimensionId,
        cx: int,
        cz: int,
    ) -> None:
        super().__init__(level_ref)
        self._lock = RLock()
        self._dimension_id = dimension_id
        self._key = ChunkKey(cx, cz)
        self._chunk_history = chunk_history
        self._chunk_data_history = chunk_data_history
        self._raw_dimension = None

    changed = Signal[()]()

    @property
    def dimension_id(self) -> DimensionId:
        return self._dimension_id

    @property
    def cx(self) -> int:
        return self._key.cx

    @property
    def cz(self) -> int:
        return self._key.cz

    def _get_raw_dimension(self) -> RawDimensionT:
        if self._raw_dimension is None:
            self._raw_dimension = self._l.raw.get_dimension(self.dimension_id)
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
        components: Iterable[str] | None = None,
        blocking: bool = True,
        timeout: float = -1,
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
        with self.lock(blocking=blocking, timeout=timeout):
            chunk = self.get(components)
            yield chunk
            # If an exception occurs in user code, this line won't be run.
            self._set(chunk)
        self.changed.emit()
        self._l.changed.emit()

    def exists(self) -> bool:
        """
        Does the chunk exist. This is a quick way to check if the chunk exists without loading it.

        This state may change if the lock is not acquired.

        :return: True if the chunk exists. Calling get on this chunk handle may still throw ChunkLoadError
        """
        if self._chunk_history.has_resource(self._key):
            return self._chunk_history.resource_exists(self._key)
        else:
            # The history system is not aware of the chunk. Look in the level data
            return self._get_raw_dimension().has_chunk(self.cx, self.cz)

    def _preload(self) -> None:
        """Load the chunk data if it has not already been loaded."""
        if not self._chunk_history.has_resource(self._key):
            # The history system is not aware of the chunk. Load from the level data
            chunk: Chunk
            try:
                raw_chunk = self._get_raw_dimension().get_raw_chunk(self.cx, self.cz)
                chunk = self._get_raw_dimension().raw_chunk_to_native_chunk(
                    raw_chunk,
                    self.cx,
                    self.cz,
                )
            except ChunkDoesNotExist:
                self._chunk_history.set_initial_resource(self._key, b"")
            except ChunkLoadError as e:
                self._chunk_history.set_initial_resource(self._key, pickle.dumps(e))
            else:
                self._chunk_history.set_initial_resource(
                    self._key, pickle.dumps(chunk.chunk_id)
                )
                for component_id, component_data in chunk.serialise_chunk().items():
                    if component_data is None:
                        raise RuntimeError(
                            "Component must not be None when initialising chunk"
                        )
                    self._chunk_data_history.set_initial_resource(
                        b"/".join((bytes(self._key), component_id.encode())),
                        component_data,
                    )

    def _get_null_chunk(self) -> ChunkT:
        """Get a null chunk instance used for this chunk.

        :raises:
            ChunkDoesNotExist if the chunk does not exist.
        """
        data = self._chunk_history.get_resource(self._key)
        if data:
            obj: ChunkLoadError | str = pickle.loads(data)
            if isinstance(obj, ChunkLoadError):
                raise obj
            elif isinstance(obj, str):
                return get_null_chunk(obj)  # type: ignore
            else:
                raise RuntimeError
        else:
            raise ChunkDoesNotExist

    def get_class(self) -> type[ChunkT]:
        """Get the chunk class used for this chunk.

        :raises:
            ChunkDoesNotExist if the chunk does not exist.
        """
        return type(self._get_null_chunk())

    def get(self, components: Iterable[str] | None = None) -> ChunkT:
        """Get a unique copy of the chunk data.

        If you want to edit the chunk, use :meth:`edit` instead.

        If you only want to access/modify parts of the chunk data you can specify the components you want to load.
        This makes it faster because you don't need to load unneeded parts.

        :param components: None to load all components or an iterable of component strings to load.
        :return: A unique copy of the chunk data.
        """
        with self.lock(blocking=False):
            self._preload()
            chunk = self._get_null_chunk()
            if components is None:
                components = chunk.component_ids
            else:
                # Ensure all component ids are valid for this class.
                components = set(components).intersection(chunk.component_ids)
            chunk_components = dict[str, bytes | None]()
            for component_id in components:
                chunk_components[component_id] = self._chunk_data_history.get_resource(
                    b"/".join((bytes(self._key), component_id.encode()))
                )
            chunk.reconstruct_chunk(chunk_components)
            return chunk

    def _set(self, chunk: ChunkT | None) -> None:
        """Lock must be acquired before calling this"""
        history = self._chunk_history
        if not history.has_resource(self._key):
            if self._l.history_enabled:
                self._preload()
            else:
                history.set_initial_resource(self._key, b"")
        if chunk is None:
            history.set_resource(self._key, b"")
        else:
            self._validate_chunk(chunk)
            try:
                old_chunk_class = self.get_class()
            except ChunkLoadError:
                old_chunk_class = None
            new_chunk_class = type(chunk)
            component_data = chunk.serialise_chunk()
            if old_chunk_class != new_chunk_class and None in component_data.values():
                raise RuntimeError(
                    "When changing chunk class all the data must be present."
                )
            history.set_resource(self._key, pickle.dumps(new_chunk_class))
            for component_id, data in component_data.items():
                if data is None:
                    continue
                self._chunk_data_history.set_resource(
                    b"/".join((bytes(self._key), component_id.encode())),
                    data,
                )

    @staticmethod
    @abstractmethod
    def _validate_chunk(chunk: ChunkT) -> None:
        raise NotImplementedError

    def set(self, chunk: ChunkT) -> None:
        """
        Overwrite the chunk data.
        You must acquire the chunk lock before setting.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        :raises:
            LockNotAcquired: If the chunk is already locked by another thread.
        """
        with self.lock(blocking=False):
            self._set(chunk)
        self.changed.emit()
        self._l.changed.emit()

    def delete(self) -> None:
        """Delete the chunk from the level."""
        with self.lock(blocking=False):
            self._set(None)
        self.changed.emit()
        self._l.changed.emit()

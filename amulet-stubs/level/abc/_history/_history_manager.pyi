from ._cache import GlobalDiskCache as GlobalDiskCache
from _typeshed import Incomplete
from amulet.utils.signal import Signal as Signal
from threading import Lock
from typing import Any, Generic, Mapping, Protocol, Sequence, TypeVar
from weakref import WeakSet, WeakValueDictionary

class ResourceId(Protocol):
    def __hash__(self) -> int:
        """A constant hash"""
    def __eq__(self, other: Any) -> bool: ...
    def __bytes__(self) -> bytes:
        """A constant bytes representation"""
ResourceIdT = TypeVar('ResourceIdT', bound=ResourceId)

class Resource:
    __slots__: Incomplete
    index: int
    saved_index: int
    global_index: int
    exists: Incomplete
    def __init__(self) -> None: ...
    def get_resource_key(self, uuid: bytes, resource_id: ResourceId) -> bytes: ...

class HistoryManagerPrivate:
    lock: Lock
    resources: WeakValueDictionary[bytes, dict[ResourceId, Resource]]
    history: list[WeakSet[Resource]]
    history_index: int
    has_redo: bool
    cache: GlobalDiskCache
    def __init__(self) -> None: ...
    def invalidate_future(self) -> None:
        """Destroy all future redo bins. Caller must acquire the lock"""
    def reset(self) -> None: ...

class HistoryManager:
    __slots__: Incomplete
    _h: HistoryManagerPrivate
    def __init__(self) -> None: ...
    def new_layer(self) -> HistoryManagerLayer: ...
    history_changed: Incomplete
    def create_undo_bin(self) -> None:
        """
        Call this to create a new undo bin.
        All changes made after this point will be part of the same undo bin until this is called again.
        If this is not called, all changes will be part of the previous undo bin.
        """
    def mark_saved(self) -> None: ...
    @property
    def undo_count(self) -> int:
        """The number of times undo can be called."""
    def undo(self) -> None:
        """Undo the changes in the current undo bin."""
    def _redo_count(self) -> int: ...
    @property
    def redo_count(self) -> int:
        """The number of times redo can be called."""
    def redo(self) -> None:
        """Redo the changes in the next undo bin."""
    def reset(self) -> None:
        """Reset to the factory state."""

class HistoryManagerLayer(Generic[ResourceIdT]):
    __slots__: Incomplete
    _h: HistoryManagerPrivate
    _uuid: bytes
    _resources: dict[ResourceIdT, Resource]
    def __init__(self, _h: HistoryManagerPrivate, uuid: bytes, resources: dict[ResourceIdT, Resource]) -> None:
        """This must not be used directly."""
    def resources(self) -> Sequence[ResourceIdT]:
        """
        Get all resource ids from this layer.
        :return:
        """
    def changed_resources(self) -> Sequence[ResourceIdT]:
        """
        Get all resource ids from this layer that have changed since the last call to mark_saved.
        :return:
        """
    def resources_exist_map(self) -> Mapping[ResourceIdT, bool]:
        """
        Get a mapping from the resource ids to a bool stating if the data exists for that resource.
        If false that resource has been deleted.
        """
    def has_resource(self, resource_id: ResourceIdT) -> bool:
        """
        Check if a resource entry exists.
        If the resource has been loaded this will be True regardless if the resource data has been deleted.
        Use :meth:`resource_exists` to check if the resource data has been deleted.
        Calling :meth:`get_resource` or :meth:`set_resource` when this is False will error.
        :param resource_id: The resource identifier
        :return:
        """
    def resource_exists(self, resource_id: ResourceIdT) -> bool:
        """
        A fast way to check if the resource data exists without loading it.
        :param resource_id: The resource identifier
        :return: True if the data exists.
        """
    def get_resource(self, resource_id: ResourceIdT) -> bytes:
        """
        Get the newest resource data.
        :param resource_id: The resource identifier
        :return: The binary data that was previously set. An empty bytes object for the deleted state.
        """
    def set_initial_resource(self, resource_id: ResourceIdT, data: bytes) -> None:
        """
        Set the data for the resource.
        This can only be used if the resource does not already exist.
        :param resource_id: The resource identifier
        :param data: The binary data to set. An empty bytes object for the deleted state.
        :return:
        """
    def set_resource(self, resource_id: ResourceIdT, data: bytes) -> None:
        """
        Set the data for the resource.
        :param resource_id: The resource identifier
        :param data: The binary data to set. An empty bytes object for the deleted state.
        :return:
        """

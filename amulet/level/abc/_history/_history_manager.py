from __future__ import annotations

from uuid import uuid4
from threading import Lock
from typing import Sequence, Protocol, TypeVar, Generic, Mapping, Any
from weakref import WeakSet, WeakValueDictionary
from collections.abc import MutableMapping

from amulet.utils.signal import Signal, SignalInstanceCacheName

from ._cache import GlobalDiskCache

# TODO: consider adding a max undo option
# TODO: if we clear old undo info we should remove that data from the cache
# TODO: compact the cache periodically


class ResourceId(Protocol):
    def __hash__(self) -> int:
        """A constant hash"""
        ...

    def __eq__(self, other: Any) -> bool: ...

    def __bytes__(self) -> bytes:
        """A constant bytes representation"""
        ...


ResourceIdT = TypeVar("ResourceIdT", bound=ResourceId)


class Resource:
    __slots__ = ("index", "saved_index", "global_index", "exists")

    def __init__(self) -> None:
        # The index of the currently active revision
        self.index: int = 0
        # The index of the saved revision. -1 if the index no longer exists (overwritten or destroyed future)
        self.saved_index: int = 0
        # The global history index
        self.global_index: int = 0
        # Does the resource data exist
        self.exists: list[bool] = [True]

    def get_resource_key(self, uuid: bytes, resource_id: ResourceId) -> bytes:
        return b"/".join((uuid, bytes(resource_id), str(self.index).encode()))


class HistoryManagerPrivate:
    lock: Lock
    resources: WeakValueDictionary[bytes, MutableMapping[ResourceId, Resource]]
    history: list[WeakSet[Resource]]
    history_index: int
    has_redo: bool
    cache: GlobalDiskCache

    def __init__(self) -> None:
        self.lock = Lock()
        self.resources = WeakValueDictionary()
        self.history = [WeakSet()]
        self.history_index = 0
        self.has_redo = False
        self.cache = GlobalDiskCache.instance()

    def invalidate_future(self) -> None:
        """Destroy all future redo bins. Caller must acquire the lock"""
        if self.has_redo:
            self.has_redo = False
            del self.history[self.history_index + 1 :]
            for layer in self.resources.values():
                for resource in layer.values():
                    if resource.saved_index > resource.index:
                        # A future index is saved that just got invalidated
                        resource.saved_index = -1

    def reset(self) -> None:
        with self.lock:
            for layer in self.resources.values():
                layer.clear()
            self.history = [WeakSet()]
            self.history_index = 0
            self.has_redo = False


class CustomDict(dict):
    pass


class HistoryManager:
    __slots__ = (SignalInstanceCacheName, "_h")

    _h: HistoryManagerPrivate

    def __init__(self) -> None:
        self._h = HistoryManagerPrivate()

    def new_layer(self) -> HistoryManagerLayer:
        uuid = uuid4().bytes
        resources: MutableMapping[ResourceId, Resource] = CustomDict()
        self._h.resources[uuid] = resources
        return HistoryManagerLayer(self._h, uuid, resources)

    history_changed = Signal[()]()

    def create_undo_bin(self) -> None:
        """
        Call this to create a new undo bin.
        All changes made after this point will be part of the same undo bin until this is called again.
        If this is not called, all changes will be part of the previous undo bin.
        """
        with self._h.lock:
            self._h.invalidate_future()
            self._h.history_index += 1
            self._h.history.append(WeakSet())

    def mark_saved(self) -> None:
        with self._h.lock:
            for layer in self._h.resources.values():
                for resource in layer.values():
                    resource.saved_index = resource.index

    @property
    def undo_count(self) -> int:
        """The number of times undo can be called."""
        with self._h.lock:
            return self._h.history_index

    def undo(self) -> None:
        """Undo the changes in the current undo bin."""
        with self._h.lock:
            if self._h.history_index <= 0:
                raise RuntimeError
            for resource in self._h.history[self._h.history_index]:
                resource.index -= 1
            self._h.history_index -= 1
            self._h.has_redo = True

    def _redo_count(self) -> int:
        return len(self._h.history) - (self._h.history_index + 1)

    @property
    def redo_count(self) -> int:
        """The number of times redo can be called."""
        with self._h.lock:
            return self._redo_count()

    def redo(self) -> None:
        """Redo the changes in the next undo bin."""
        with self._h.lock:
            if not self._h.has_redo:
                raise RuntimeError
            self._h.history_index += 1
            for resource in self._h.history[self._h.history_index]:
                resource.index += 1
            self._h.has_redo = bool(self._redo_count())

    def reset(self) -> None:
        """Reset to the factory state."""
        self._h.reset()


class HistoryManagerLayer(Generic[ResourceIdT]):
    __slots__ = ("_h", "_uuid", "_resources")

    _h: HistoryManagerPrivate
    _uuid: bytes
    _resources: MutableMapping[ResourceIdT, Resource]

    def __init__(
        self,
        _h: HistoryManagerPrivate,
        uuid: bytes,
        resources: MutableMapping[ResourceIdT, Resource],
    ) -> None:
        """This must not be used directly."""
        self._h = _h
        self._uuid = uuid
        self._resources = resources

    def resources(self) -> Sequence[ResourceIdT]:
        """
        Get all resource ids from this layer.
        :return:
        """
        with self._h.lock:
            return list(self._resources)

    def changed_resources(self) -> Sequence[ResourceIdT]:
        """
        Get all resource ids from this layer that have changed since the last call to mark_saved.
        :return:
        """
        with self._h.lock:
            return [
                resource_id
                for resource_id, resource in self._resources.items()
                if resource.saved_index != resource.index
            ]

    def resources_exist_map(self) -> Mapping[ResourceIdT, bool]:
        """
        Get a mapping from the resource ids to a bool stating if the data exists for that resource.
        If false that resource has been deleted.
        """
        with self._h.lock:
            return {
                resource_id: resource.exists[resource.index]
                for resource_id, resource in self._resources.items()
            }

    def has_resource(self, resource_id: ResourceIdT) -> bool:
        """
        Check if a resource entry exists.
        If the resource has been loaded this will be True regardless if the resource data has been deleted.
        Use :meth:`resource_exists` to check if the resource data has been deleted.
        Calling :meth:`get_resource` or :meth:`set_resource` when this is False will error.
        :param resource_id: The resource identifier
        :return:
        """
        with self._h.lock:
            return resource_id in self._resources

    def resource_exists(self, resource_id: ResourceIdT) -> bool:
        """
        A fast way to check if the resource data exists without loading it.
        :param resource_id: The resource identifier
        :return: True if the data exists.
        """
        with self._h.lock:
            resource = self._resources[resource_id]
            return resource.exists[resource.index]

    def get_resource(self, resource_id: ResourceIdT) -> bytes:
        """
        Get the newest resource data.
        :param resource_id: The resource identifier
        :return: The binary data that was previously set. An empty bytes object for the deleted state.
        """
        with self._h.lock:
            resource = self._resources[resource_id]
            if resource.exists[resource.index]:
                return self._h.cache[resource.get_resource_key(self._uuid, resource_id)]
            else:
                return b""

    def set_initial_resource(self, resource_id: ResourceIdT, data: bytes) -> None:
        """
        Set the data for the resource.
        This can only be used if the resource does not already exist.
        :param resource_id: The resource identifier
        :param data: The binary data to set. An empty bytes object for the deleted state.
        :return:
        """
        with self._h.lock:
            if resource_id in self._resources:
                raise RuntimeError("Resource already exists")
            resource = self._resources[resource_id] = Resource()
            if data:
                # Save the data to the cache if it exists
                self._h.cache[resource.get_resource_key(self._uuid, resource_id)] = data
            # Store a flag if it exists
            resource.exists[resource.index] = bool(data)

    def set_resource(self, resource_id: ResourceIdT, data: bytes) -> None:
        """
        Set the data for the resource.
        :param resource_id: The resource identifier
        :param data: The binary data to set. An empty bytes object for the deleted state.
        :return:
        """
        with self._h.lock:
            self._h.invalidate_future()
            resource = self._resources[resource_id]
            if resource.global_index != self._h.history_index:
                # The global history index has been increased since the last change to this resource
                # Add a new state
                resource.index += 1
                resource.global_index = self._h.history_index
                resource.exists.append(False)
            if resource.index == resource.saved_index:
                # The saved index has been directly modified
                resource.saved_index = -1
            if data:
                # Save the data to the cache if it exists
                self._h.cache[resource.get_resource_key(self._uuid, resource_id)] = data
            # Store a flag if it exists
            resource.exists[resource.index] = bool(data)
            if self._h.history_index:
                # Add the resource to the history bin if one has been created
                self._h.history[self._h.history_index].add(resource)

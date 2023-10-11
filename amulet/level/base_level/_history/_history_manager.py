from __future__ import annotations

from uuid import uuid4
from threading import Lock
from typing import Sequence, Protocol, TypeVar, Generic, Mapping
from weakref import WeakSet, WeakValueDictionary

from amulet.utils.signal import Signal

from ._cache import GlobalDiskCache

# TODO: consider adding a max undo option
# TODO: if we clear old undo info we should remove that data from the cache
# TODO: compact the cache periodically


class ResourceId(Protocol):
    def __hash__(self) -> int:
        """A constant hash"""
        ...

    def __eq__(self, other) -> bool:
        ...

    def __bytes__(self) -> bytes:
        """A constant bytes representation"""
        ...


class Resource:
    __slots__ = ("index", "saved_index", "global_index", "exists")

    def __init__(self):
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
    def __init__(self):
        self.lock = Lock()
        self.resources: WeakValueDictionary[bytes, dict[ResourceId, Resource]] = WeakValueDictionary()
        self.history: list[WeakSet[Resource]] = [WeakSet()]
        self.history_index = 0
        self.has_redo = False
        self.cache = GlobalDiskCache.instance()

    def invalidate_future(self):
        """Destroy all future redo bins. Caller must acquire the lock"""
        if self.has_redo:
            self.has_redo = False
            del self.history[self.history_index + 1 :]
            for layer in self.resources.values():
                for resource in layer.values():
                    if resource.saved_index > resource.index:
                        # A future index is saved that just got invalidated
                        resource.saved_index = -1

    def reset(self):
        with self.lock:
            for layer in self.resources.values():
                layer.clear()
            self.history = [WeakSet()]
            self.history_index = 0
            self.has_redo = False


ResourceIdT = TypeVar("ResourceIdT", bound=ResourceId)


class HistoryManager:
    __slots__ = ("_d",)

    def __init__(self):
        self._d = HistoryManagerPrivate()

    def new_layer(self) -> HistoryManagerLayer:
        return HistoryManagerLayer(self._d)

    history_changed = Signal()

    def create_undo_bin(self):
        """
        Call this to create a new undo bin.
        All changes made after this point will be part of the same undo bin until this is called again.
        If this is not called, all changes will be part of the previous undo bin.
        """
        with self._d.lock:
            self._d.invalidate_future()
            self._d.history_index += 1
            self._d.history.append(WeakSet())

    def mark_saved(self):
        with self._d.lock:
            for layer in self._d.resources.values():
                for resource in layer.values():
                    resource.saved_index = resource.index

    @property
    def undo_count(self) -> int:
        """The number of times undo can be called."""
        with self._d.lock:
            return self._d.history_index

    def undo(self):
        """Undo the changes in the current undo bin."""
        with self._d.lock:
            if self._d.history_index <= 0:
                raise RuntimeError
            for resource in self._d.history[self._d.history_index]:
                resource.index -= 1
            self._d.history_index -= 1
            self._d.has_redo = True

    def _redo_count(self) -> int:
        return len(self._d.history) - (self._d.history_index + 1)

    @property
    def redo_count(self) -> int:
        """The number of times redo can be called."""
        with self._d.lock:
            return self._redo_count()

    def redo(self):
        """Redo the changes in the next undo bin."""
        with self._d.lock:
            if not self._d.has_redo:
                raise RuntimeError
            self._d.history_index += 1
            for resource in self._d.history[self._d.history_index]:
                resource.index += 1
            self._d.has_redo = bool(self._redo_count())

    def reset(self):
        """Reset to the factory state."""
        self._d.reset()


class HistoryManagerLayer(Generic[ResourceIdT]):
    __slots__ = ("_d", "_uuid", "_resources")

    def __init__(self, _d: HistoryManagerPrivate):
        self._d = _d
        self._uuid = uuid4().bytes
        self._resources: dict[ResourceIdT, Resource] = {}
        self._d.resources[self._uuid] = self._resources

    def resources(self) -> Sequence[ResourceIdT]:
        """
        Get all resource ids from this layer.
        :return:
        """
        with self._d.lock:
            return list(self._resources)

    def changed_resources(self) -> Sequence[ResourceIdT]:
        """
        Get all resource ids from this layer that have changed since the last call to mark_saved.
        :return:
        """
        with self._d.lock:
            return [
                resource_id
                for resource_id, resource in self._resources
                if resource.saved_index != resource.index
            ]

    def resources_exist(self) -> Mapping[ResourceIdT, bool]:
        """
        Get a mapping from the resource ids to a bool stating if the data exists for that resource.
        If false that resource has been deleted.
        """
        with self._d.lock:
            return {
                resource_id: resource.exists[resource.index]
                for resource_id, resource in self._resources
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
        with self._d.lock:
            return resource_id in self._resources

    def resource_exists(self, resource_id: ResourceIdT) -> bool:
        """
        A fast way to check if the resource data exists without loading it.
        :param resource_id: The resource identifier
        :return: True if the data exists.
        """
        with self._d.lock:
            resource = self._resources[resource_id]
            return resource.exists[resource.index]

    def get_resource(self, resource_id: ResourceIdT) -> bytes:
        """
        Get the newest resource data.
        :param resource_id: The resource identifier
        :return: The binary data that was previously set. An empty bytes object for the deleted state.
        """
        with self._d.lock:
            resource = self._resources[resource_id]
            if resource.exists[resource.index]:
                return self._d.cache[resource.get_resource_key(self._uuid, resource_id)]
            else:
                return b""

    def set_initial_resource(self, resource_id: ResourceIdT, data: bytes):
        """
        Set the data for the resource.
        This can only be used if the resource does not already exist.
        :param resource_id: The resource identifier
        :param data: The binary data to set. An empty bytes object for the deleted state.
        :return:
        """
        with self._d.lock:
            if resource_id in self._resources:
                raise RuntimeError("Resource already exists")
            resource = self._resources[resource_id] = Resource()
            if data:
                # Save the data to the cache if it exists
                self._d.cache[resource.get_resource_key(self._uuid, resource_id)] = data
            # Store a flag if it exists
            resource.exists[resource.index] = bool(data)

    def set_resource(self, resource_id: ResourceIdT, data: bytes):
        """
        Set the data for the resource.
        :param resource_id: The resource identifier
        :param data: The binary data to set. An empty bytes object for the deleted state.
        :return:
        """
        with self._d.lock:
            self._d.invalidate_future()
            resource = self._resources[resource_id]
            if resource.global_index != self._d.history_index:
                # The global history index has been increased since the last change to this resource
                # Add a new state
                resource.index += 1
                resource.global_index = self._d.history_index
                resource.exists.append(False)
            if resource.index == resource.saved_index:
                # The saved index has been directly modified
                resource.saved_index = -1
            if data:
                # Save the data to the cache if it exists
                self._d.cache[resource.get_resource_key(self._uuid, resource_id)] = data
            # Store a flag if it exists
            resource.exists[resource.index] = bool(data)
            if self._d.history_index:
                # Add the resource to the history bin if one has been created
                self._d.history[self._d.history_index].add(resource)

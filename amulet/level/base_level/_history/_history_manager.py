from __future__ import annotations

from uuid import uuid4
from threading import Lock
from typing import Sequence, Protocol, TypeVar, Generic

from amulet.utils.signal import Signal

from ._cache import GlobalDiskCache


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
    __slots__ = ("index", "saved_index", "global_index")

    def __init__(self):
        # The index of the currently active revision
        self.index: int = -1
        # The index of the saved revision. -2 if the index no longer exists (overwritten or destroyed future)
        self.saved_index: int = -1
        # The global history index
        self.global_index: int = -1

    def get_resource_key(self, uuid: bytes, resource_id: ResourceId) -> bytes:
        return b"/".join((uuid, bytes(resource_id), str(self.index).encode()))


class HistoryManagerPrivate:
    def __init__(self):
        self.lock = Lock()
        self.resources: dict[bytes, dict[ResourceId, Resource]] = {}
        self.history: list[set[Resource]] = []
        self.history_index = -1
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
                        resource.saved_index = -2


ResourceIdT = TypeVar("ResourceIdT", bound=ResourceId)


class HistoryManager:
    __slots__ = ("_d",)

    def __init__(self):
        self._d = HistoryManagerPrivate()

    def new_layer(self) -> HistoryManagerLayer:
        return HistoryManagerLayer(self._d)

    history_change = Signal()

    def create_undo_bin(self):
        """
        Call this to create a new undo bin.
        All changes made after this point will be part of the same undo bin until this is called again.
        If this is not called, all changes will be part of the previous undo bin.
        """
        with self._d.lock:
            self._d.invalidate_future()
            self._d.history_index += 1
            self._d.history.append(set())

    def mark_saved(self):
        with self._d.lock:
            for layer in self._d.resources.values():
                for resource in layer.values():
                    resource.saved_index = resource.index

    @property
    def undo_count(self) -> int:
        """The number of times undo can be called."""
        with self._d.lock:
            return self._d.history_index + 1

    def undo(self):
        """Undo the changes in the current undo bin."""
        with self._d.lock:
            if self._d.history_index < 0:
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


class HistoryManagerLayer(Generic[ResourceIdT]):
    __slots__ = ("_d", "_uuid")

    def __init__(self, _d: HistoryManagerPrivate):
        self._d = _d
        self._uuid = uuid4().bytes
        self._d.resources[self._uuid] = {}

    def has_resource(self, resource_id: ResourceIdT) -> bool:
        """
        Check if a resource entry exists.
        :param resource_id: The identifier for the resource in the data group e.g. b"minecraft:overworld/10/50"
        :return:
        """
        with self._d.lock:
            return resource_id in self._d.resources[self._uuid]

    def get_resource(self, resource_id: ResourceIdT) -> bytes:
        """
        Get the newest resource data.
        :param resource_id: The identifier for the resource in the data group e.g. b"minecraft:overworld/10/50"
        :return:
        """
        with self._d.lock:
            resource = self._d.resources[self._uuid][resource_id]
            return self._d.cache[resource.get_resource_key(self._uuid, resource_id)]

    def set_initial_resource(self, resource_id: ResourceIdT, data: bytes):
        """
        Set the data for the resource. This must only be used if the resource does not already exist.
        :param resource_id: The identifier for the resource in the data group e.g. b"minecraft:overworld/10/50"
        :param data: The binary data to set.
        :return:
        """
        with self._d.lock:
            layer = self._d.resources[self._uuid]
            if resource_id in layer:
                raise RuntimeError("Resource already exists")
            resource = layer[resource_id] = Resource()
            self._d.cache[resource.get_resource_key(self._uuid, resource_id)] = data

    def set_resource(self, resource_id: ResourceIdT, data: bytes):
        """
        Set the data for the resource.
        :param resource_id: The identifier for the resource in the data group e.g. b"minecraft:overworld/10/50"
        :param data: The binary data to set.
        :return:
        """
        with self._d.lock:
            self._d.invalidate_future()
            resource = self._d.resources[self._uuid][resource_id]
            if resource.global_index != self._d.history_index:
                resource.index += 1
                resource.global_index = self._d.history_index
            if resource.index == resource.saved_index:
                resource.saved_index = -2
            self._d.cache[resource.get_resource_key(self._uuid, resource_id)] = data
            if self._d.history_index != -1:
                self._d.history[self._d.history_index].add(resource)

    def get_changed_resource_ids(self) -> Sequence[ResourceIdT]:
        """
        Get resource ids in the data layer for all resources that have changed since the last call to mark_saved.
        :return:
        """
        with self._d.lock:
            return [
                resource_id
                for resource_id, resource in self._d.resources[self._uuid]
                if resource.saved_index != resource.index
            ]

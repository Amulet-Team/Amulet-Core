"""
Get the current history index
Undo
Redo
Add new history index
Retrieve history items
    mapping from key and current history index to resource id


"""

from uuid import uuid4
from threading import Lock
from typing import Optional, Sequence
from amulet.utils.signal import Signal

from ._cache import GlobalDiskCache


class Resource:
    __slots__ = ("index", "saved_index", "global_index")

    def __init__(self):
        # The index of the currently active revision
        self.index: int = -1
        # The index of the saved revision. -2 if the index no longer exists (overwritten or destroyed future)
        self.saved_index: int = -1
        # The global history index
        self.global_index: int = -1

    def get_resource_key(
        self, uuid: bytes, data_layer: bytes, resource_id: bytes
    ) -> bytes:
        return b"/".join((uuid, data_layer, resource_id, str(self.index).encode()))


class HistoryManager:
    def __init__(self):
        self._lock = Lock()
        self._uuid = uuid4().bytes
        self._resources: dict[bytes, dict[bytes, Resource]] = {}
        self._history: list[set[Resource]] = []
        self._history_index = -1
        self._has_redo = False
        self._cache = GlobalDiskCache()

    history_change = Signal()

    def has_resource(self, data_layer: bytes, resource_id: bytes) -> bool:
        """
        Get the newest resource data.
        :param data_layer: The group the data exists in e.g. b"chunks"
        :param resource_id: The identifier for the resource in the data group e.g. b"minecraft:overworld/10/50"
        :return:
        """
        with self._lock:
            return (
                data_layer in self._resources
                and resource_id in self._resources[data_layer]
            )

    def get_resource(self, data_layer: bytes, resource_id: bytes) -> bytes:
        """
        Get the newest resource data.
        :param data_layer: The group the data exists in e.g. b"chunks"
        :param resource_id: The identifier for the resource in the data group e.g. b"minecraft:overworld/10/50"
        :return:
        """
        with self._lock:
            resource = self._resources[data_layer][resource_id]
            return self._cache[
                resource.get_resource_key(self._uuid, data_layer, resource_id)
            ]

    def set_initial_resource(self, data_layer: bytes, resource_id: bytes, data: bytes):
        """
        Set the data for the resource. This must only be used if the resource does not already exist.
        :param data_layer: The group the data exists in e.g. b"chunks"
        :param resource_id: The identifier for the resource in the data group e.g. b"minecraft:overworld/10/50"
        :param data: The binary data to set.
        :return:
        """
        with self._lock:
            layer = self._resources.setdefault(data_layer, {})
            if resource_id in layer:
                raise RuntimeError("Resource already exists")
            resource = layer[resource_id] = Resource()
            self._cache[
                resource.get_resource_key(self._uuid, data_layer, resource_id)
            ] = data

    def set_resource(self, data_layer: bytes, resource_id: bytes, data: bytes):
        """
        Set the data for the resource.
        :param data_layer: The group the data exists in e.g. b"chunks"
        :param resource_id: The identifier for the resource in the data group e.g. b"minecraft:overworld/10/50"
        :param data: The binary data to set.
        :return:
        """
        with self._lock:
            self._invalidate_future()
            resource = self._resources[data_layer][resource_id]
            if resource.global_index != self._history_index:
                resource.index += 1
                resource.global_index = self._history_index
            if resource.index == resource.saved_index:
                resource.saved_index = -2
            self._cache[
                resource.get_resource_key(self._uuid, data_layer, resource_id)
            ] = data
            if self._history_index != -1:
                self._history[self._history_index].add(resource)

    def create_undo_bin(self):
        """
        Call this to create a new undo bin.
        All changes made after this point will be part of the same undo bin until this is called again.
        If this is not called, all changes will be part of the previous undo bin.
        """
        with self._lock:
            self._invalidate_future()
            self._history_index += 1
            self._history.append(set())

    def _invalidate_future(self):
        """Destroy all future redo bins. Caller must acquire the lock"""
        if self._has_redo:
            self._has_redo = False
            del self._history[self._history_index + 1 :]
            for layer in self._resources.values():
                for resource in layer.values():
                    if resource.saved_index > resource.index:
                        # A future index is saved that just got invalidated
                        resource.saved_index = -2

    def get_changed_resource_ids(self, data_layer: bytes) -> Sequence[bytes]:
        """
        Get resource ids in the data layer for all resources that have changed since the last call to mark_saved.
        :param data_layer: The group the data exists in e.g. b"chunks"
        :return:
        """
        with self._lock:
            return [
                resource_id
                for resource_id, resource in self._resources[data_layer]
                if resource.saved_index != resource.index
            ]

    def mark_saved(self):
        with self._lock:
            for layer in self._resources.values():
                for resource in layer.values():
                    resource.saved_index = resource.index

    @property
    def undo_count(self) -> int:
        """The number of times undo can be called."""
        with self._lock:
            return self._history_index + 1

    def undo(self):
        """Undo the changes in the current undo bin."""
        with self._lock:
            if self._history_index < 0:
                raise RuntimeError
            for resource in self._history[self._history_index]:
                resource.index -= 1
            self._history_index -= 1
            self._has_redo = True

    def _redo_count(self) -> int:
        return len(self._history) - (self._history_index + 1)

    @property
    def redo_count(self) -> int:
        """The number of times redo can be called."""
        with self._lock:
            return self._redo_count()

    def redo(self):
        """Redo the changes in the next undo bin."""
        with self._lock:
            if not self._has_redo:
                raise RuntimeError
            self._history_index += 1
            for resource in self._history[self._history_index]:
                resource.index += 1
            self._has_redo = bool(self._redo_count())

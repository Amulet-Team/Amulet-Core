from typing import Tuple, Generator

from amulet.utils.generator import generator_unpacker
from amulet.api.history.base.history_manager import HistoryManager
from .container import ContainerHistoryManager

SnapshotType = Tuple[HistoryManager, ...]


class MetaHistoryManager(ContainerHistoryManager):
    def __init__(self):
        super().__init__()
        self._world_managers = []
        self._non_world_managers = []

    def _check_snapshot(self, snapshot: SnapshotType):
        assert isinstance(snapshot, tuple) and all(
            isinstance(item, HistoryManager) for item in snapshot
        )

    def register(self, manager: HistoryManager, is_world_manager: bool):
        """
        Register a manager to track.
        :param manager: The manager to track
        :param is_world_manager: Is the manager tracking world data
        :return:
        """
        assert isinstance(
            manager, HistoryManager
        ), "manager must be an instance of BaseHistoryManager"
        if is_world_manager:
            self._world_managers.append(manager)
        else:
            self._non_world_managers.append(manager)

    def _undo(self, snapshot: SnapshotType):
        for item in snapshot:
            item.undo()

    def _redo(self, snapshot: SnapshotType):
        for item in snapshot:
            item.redo()

    def _mark_saved(self):
        for manager in self._managers():
            manager.mark_saved()

    def _managers(
        self, world: bool = True, non_world: bool = True
    ) -> Tuple[HistoryManager, ...]:
        return (
            tuple(self._world_managers) * world
            + tuple(self._non_world_managers) * non_world
        )

    @property
    def changed(self) -> bool:
        if super().changed:
            return True
        managers = self._managers(True, False)
        for manager in managers:
            if manager.changed:
                return True
        return False

    def create_undo_point(self, world=True, non_world=True) -> bool:
        return generator_unpacker(self.create_undo_point_iter(world, non_world))

    def create_undo_point_iter(
        self, world=True, non_world=True
    ) -> Generator[float, None, bool]:
        """Create an undo point.

        :param world: Should the world based history managers be included
        :param non_world: Should the non-world based history managers be included
        :return:
        """
        managers = self._managers(world, non_world)
        snapshot = []
        for manager in managers:
            changed = yield from manager.create_undo_point_iter()
            if changed:
                snapshot.append(manager)
        return self._register_snapshot(tuple(snapshot))

    def restore_last_undo_point(self):
        for manager in self._managers():
            manager.restore_last_undo_point()

    def purge(self):
        """Unload all history data. Restore to the state after creation."""
        for manager in self._managers():
            manager.purge()

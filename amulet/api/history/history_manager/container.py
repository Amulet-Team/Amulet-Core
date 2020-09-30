from typing import List, Any

from amulet.api.history.base.history_manager import HistoryManager

SnapshotType = Any


class ContainerHistoryManager(HistoryManager):
    def __init__(self):
        self._snapshots: List[SnapshotType] = []
        self._snapshot_index: int = -1

        # the snapshot that was saved or the save branches off from
        self._last_save_snapshot = -1
        self._branch_save_count = 0  # if the user saves, undoes and does a new operation a save branch will be lost
        # This is the number of changes on that branch

    def _check_snapshot(self, snapshot: SnapshotType):
        raise NotImplementedError

    def _register_snapshot(self, snapshot: SnapshotType) -> bool:
        self._check_snapshot(snapshot)
        if snapshot:
            if self._last_save_snapshot > self._snapshot_index:
                # if the user has undone changes and made more changes things get a bit messy
                # This fixes the property storing the number of changes since the last save.
                self._branch_save_count += (
                    self._last_save_snapshot - self._snapshot_index
                )
                self._last_save_snapshot = self._snapshot_index
            self._snapshot_index += 1
            # delete all upstream snapshots
            del self._snapshots[self._snapshot_index :]
            self._snapshots.append(snapshot)
            return True
        return False

    def mark_saved(self):
        """Let the class know that the current state has been saved."""
        self._last_save_snapshot = self._snapshot_index
        self._branch_save_count = 0
        self._mark_saved()

    def _mark_saved(self):
        raise NotImplementedError

    @property
    def undo_count(self) -> int:
        return self._snapshot_index + 1

    @property
    def redo_count(self) -> int:
        return len(self._snapshots) - (self._snapshot_index + 1)

    @property
    def unsaved_changes(self) -> int:
        """The number of changes that have been made since the last save"""
        return (
            abs(self._snapshot_index - self._last_save_snapshot)
            + self._branch_save_count
        )

    def undo(self):
        """Undoes the last set of changes to the database"""
        if self.undo_count > 0:
            snapshot = self._snapshots[self._snapshot_index]
            self._undo(snapshot)
            self._snapshot_index -= 1

    def _undo(self, snapshot: SnapshotType):
        raise NotImplementedError

    def redo(self):
        """Redoes the last set of changes to the database"""
        if self.redo_count > 0:
            self._snapshot_index += 1
            snapshot = self._snapshots[self._snapshot_index]
            self._redo(snapshot)

    def _redo(self, snapshot: SnapshotType):
        raise NotImplementedError

    @property
    def changed(self) -> bool:
        return bool(self.unsaved_changes)

    def create_undo_point(self) -> bool:
        raise NotImplementedError

    def restore_last_undo_point(self):
        raise NotImplementedError

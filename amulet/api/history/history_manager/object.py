from typing import Optional, Any

from amulet.api.history import Changeable
from ..base import RevisionManager
from amulet.api.history.base.history_manager import HistoryManager
from ..revision_manager import RAMRevisionManager


class ObjectHistoryManager(HistoryManager):
    def __init__(self, original_entry: Changeable):
        super().__init__()
        self._value: Changeable = original_entry
        self._revision_manager = self._create_new_revision_manager(
            self._pack_value(self._value)
        )
        self._snapshots_size: int = 0
        self._snapshot_index: int = -1

        # the snapshot that was saved or the save branches off from
        self._last_save_snapshot = -1
        self._branch_save_count = 0  # if the user saves, undoes and does a new operation a save branch will be lost
        # This is the number of changes on that branch

    @property
    def value(self):
        return self._value

    @staticmethod
    def _create_new_revision_manager(original_entry: Optional[Any]) -> RevisionManager:
        """Create an RevisionManager as desired and populate it with the original entry."""
        return RAMRevisionManager(original_entry)

    def _register_snapshot(self):
        if self._last_save_snapshot > self._snapshot_index:
            # if the user has undone changes and made more changes things get a bit messy
            # This fixes the property storing the number of changes since the last save.
            self._branch_save_count += self._last_save_snapshot - self._snapshot_index
            self._last_save_snapshot = self._snapshot_index
        self._snapshot_index += 1
        self._snapshots_size = min(self._snapshots_size, self._snapshot_index) + 1

    def mark_saved(self):
        """Let the class know that the current state has been saved."""
        self._last_save_snapshot = self._snapshot_index
        self._branch_save_count = 0
        self._revision_manager.mark_saved()

    @property
    def undo_count(self) -> int:
        return self._snapshot_index + 1

    @property
    def redo_count(self) -> int:
        return self._snapshots_size - (self._snapshot_index + 1)

    @property
    def unsaved_changes(self) -> int:
        """The number of changes that have been made since the last save"""
        return (
            abs(self._snapshot_index - self._last_save_snapshot)
            + self._branch_save_count
        )

    def undo(self):
        """Undoes the last set of changes to the object"""
        if self.undo_count > 0:
            self._revision_manager.undo()
            self._unpack()
            self._snapshot_index -= 1

    def redo(self):
        """Redoes the last set of changes to the object"""
        if self.redo_count > 0:
            self._snapshot_index += 1
            self._revision_manager.redo()
            self._unpack()

    @property
    def changed(self) -> bool:
        return bool(self.unsaved_changes)

    def create_undo_point(self) -> bool:
        if self._value.changed:
            self._value.changed = False
            self._pack()
            self._register_snapshot()
            return True
        else:
            self._unpack()
            return False

    def restore_last_undo_point(self):
        self._unpack()

    def _unpack(self):
        self._value = self._revision_manager.get_current_entry()

    def _pack(self):
        self._revision_manager.put_new_entry(self._pack_value(self._value))

    def _pack_value(self, value: Optional[Any]) -> Optional[Any]:
        return value

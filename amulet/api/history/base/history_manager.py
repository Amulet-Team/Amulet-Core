from .base_history import BaseHistory


class HistoryManager(BaseHistory):
    """The base class for all active history manager objects.
    The HistoryManager tracks which objects have changed but is not aware of how they have changed."""

    def undo(self):
        """Revert to the previous state."""
        raise NotImplementedError

    def redo(self):
        """Un-revert to the next state."""
        raise NotImplementedError

    def mark_saved(self):
        """Let the class know that the current state has been saved."""
        raise NotImplementedError

    @property
    def changed(self) -> bool:
        """Have there been modifications since the last save."""
        raise NotImplementedError

    def create_undo_point(self) -> bool:
        """
        Find what has changed since the last undo point and optionally create a new undo point.
        :return: Was an undo point created. If there were no changes no snapshot will be created.
        """
        raise NotImplementedError

    def restore_last_undo_point(self):
        """Restore the world to the state it was when self.create_undo_point was called.
        If an operation errors there may be modifications made that did not get tracked.
        This will revert those changes."""
        raise NotImplementedError

    @property
    def undo_count(self) -> int:
        """The number of times the undo method can be run."""
        raise NotImplementedError

    @property
    def redo_count(self) -> int:
        """The number of times the redo method can be run."""
        raise NotImplementedError

    @property
    def unsaved_changes(self) -> int:
        """The number of changes that have been made since the last save"""
        raise NotImplementedError

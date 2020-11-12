from typing import List, Optional, Any

from .base_history import BaseHistory

StoredEntryType = Optional[Any]


class RevisionManager(BaseHistory):
    """The base API for all passive history manager objects.
    The RevisionManager stores the actual versions of the object to revert to."""

    __slots__ = ("_revisions", "_current_revision_index", "_saved_revision_index")

    def __init__(self, initial_state: StoredEntryType):
        self._revisions: List[StoredEntryType] = []  # the data for each revision
        self._current_revision_index: int = (
            0  # the index into the above for the current data
        )
        self._saved_revision_index: int = (
            0  # the index into the above for the saved version
        )
        self._store_entry(initial_state)

    @property
    def changed(self) -> bool:
        """Have there been modifications since the last save."""
        return self._current_revision_index != self._saved_revision_index

    def put_new_entry(self, entry: StoredEntryType):
        """Add a new entry to the database and increment the index."""
        if len(self._revisions) > self._current_revision_index + 1:
            # if there are upstream revisions delete them
            del self._revisions[self._current_revision_index + 1 :]
        if self._saved_revision_index > self._current_revision_index:
            # we are starting a new branch and the save was on the old branch.
            self._saved_revision_index = -1
        self._store_entry(entry)
        self._current_revision_index += 1

    def _store_entry(self, entry: StoredEntryType):
        """Store the entry data as required."""
        raise NotImplementedError

    def get_current_entry(self):
        """Get the entry at the current revision."""
        raise NotImplementedError

    def undo(self):
        """Decrement the state of the entry to the previous revision."""
        if self._current_revision_index <= 0:
            raise Exception(
                "Cannot undo past revision 0"
            )  # if run there is a bug in the code
        self._current_revision_index -= 1

    def redo(self):
        """Increment the state of the entry to the next revision."""
        if self._current_revision_index >= len(self._revisions):
            raise Exception(
                "Cannot redo past the highest revision"
            )  # if run there is a bug in the code
        self._current_revision_index += 1

    def mark_saved(self):
        """Let the class know that the current state has been saved."""
        self._saved_revision_index = self._current_revision_index

    @property
    def is_deleted(self) -> bool:
        return self._revisions[self._current_revision_index] is None

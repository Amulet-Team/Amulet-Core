import os
from typing import Optional

from amulet.api.history.base import RevisionManager
from ..data_types import EntryType


class DiskRevisionManager(RevisionManager):
    """A class to hold data about an entries history on disk.
    Revision indexes are still stored in RAM."""

    __slots__ = ("_directory",)

    def __init__(self, directory: str, initial_state: EntryType):
        self._directory: str = directory
        super().__init__(initial_state)

    def _store_entry(self, entry: EntryType):
        os.makedirs(self._directory, exist_ok=True)
        path = os.path.join(self._directory, f"{len(self._revisions)}.pickle.gz")
        path = self._serialise(path, entry)
        self._revisions.append(path)

    def _serialise(self, path: str, entry: EntryType) -> Optional[str]:
        raise NotImplementedError

    def get_current_entry(self):
        path = self._revisions[self._current_revision_index]
        return self._deserialise(path)

    def _deserialise(self, path: str) -> EntryType:
        raise NotImplementedError

from abc import abstractmethod
from typing import Optional

from amulet.api.history.base import RevisionManager
from ..data_types import EntryType


class DBRevisionManager(RevisionManager):
    """A class to hold data about an entries history on disk.
    Revision indexes are still stored in RAM."""

    __slots__ = ("_prefix",)

    def __init__(self, prefix: str, initial_state: EntryType):
        self._prefix: str = prefix
        super().__init__(initial_state)

    def _store_entry(self, entry: EntryType):
        path = f"{self._prefix}/{len(self._revisions)}"
        path = self._serialise(path, entry)
        self._revisions.append(path)

    @abstractmethod
    def _serialise(self, path: str, entry: EntryType) -> Optional[str]:
        raise NotImplementedError

    def get_current_entry(self):
        path = self._revisions[self._current_revision_index]
        return self._deserialise(path)

    @abstractmethod
    def _deserialise(self, path: str) -> EntryType:
        raise NotImplementedError

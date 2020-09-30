from amulet.api.history.base import PassiveRevisionManager
from ..data_types import EntryType


class RAMEntry(PassiveRevisionManager):
    """A class to hold data about an entries history in RAM."""

    def _store_entry(self, entry: EntryType):
        self._revisions.append(entry)

    def get_current_entry(self):
        return self._revisions[self._current_revision_index]

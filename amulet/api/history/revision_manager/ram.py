from typing import TypeVar, Optional

from amulet.api.history.base import RevisionManager
from ..changeable import Changeable

EntryT = TypeVar("EntryT", bound=Changeable)


class RAMRevisionManager(RevisionManager[EntryT]):
    """A class to hold data about an entries history in RAM."""

    def _store_entry(self, entry: Optional[EntryT]):
        self._revisions.append(entry)

    def get_current_entry(self):
        return self._revisions[self._current_revision_index]

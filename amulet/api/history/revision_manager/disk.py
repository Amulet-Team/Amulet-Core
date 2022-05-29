from abc import abstractmethod
from typing import Optional, TypeVar

from amulet.api.history.base import AbstractRevisionManager
from ..changeable import Changeable

EntryT = TypeVar("EntryT", bound=Changeable)


class AbstractDBRevisionManager(AbstractRevisionManager[EntryT]):
    """
    A class to hold data about one entry's history on disk.
    Revision indexes are still stored in RAM.
    """

    __slots__ = ("_prefix",)

    def __init__(self, prefix: str, initial_state: Optional[EntryT]):
        self._prefix: str = prefix
        super().__init__(initial_state)

    def _store_entry(self, entry: Optional[EntryT]):
        path = f"{self._prefix}/{len(self._revisions)}"
        path = self._serialise(path, entry)
        self._revisions.append(path)

    @abstractmethod
    def _serialise(self, path: str, entry: Optional[EntryT]) -> Optional[str]:
        raise NotImplementedError

    def get_current_entry(self):
        path = self._revisions[self._current_revision_index]
        return self._deserialise(path)

    @abstractmethod
    def _deserialise(self, path: str) -> Optional[EntryT]:
        raise NotImplementedError

"""
The DatabaseHistoryManager is like a dictionary that can cache historical versions of the values.
The class consists of the temporary database in RAM, the cache on disk and a way to pull from the original data source.
The temporary database:
    This is a normal dictionary in RAM.
    When accessing and modifying data this is the data you are modifying.
The cache on disk:
    This is a database on disk of the data serialised using pickle.
    This is populated with the original version of the data and each revision of the data.
    The temporary database can be cleared using the unload methods and successive get calls will re-populate the temporary database from this cache.
    As previously stated, the cache also stores historical versions of the data which enables undoing and redoing changes.
The original data source (raw form)
    This is the original data from the world/structure.
    If the data does not exist in the temporary or cache databases it will be loaded from here.
"""

from abc import abstractmethod
from typing import Tuple, Any, Dict, Generator, Iterable, Set
import threading

from amulet.api.history.data_types import EntryKeyType, EntryType
from amulet.api.history.base import RevisionManager
from amulet.api.history import Changeable
from .container import ContainerHistoryManager
from amulet.api.errors import EntryDoesNotExist, EntryLoadError
from ..revision_manager import RAMRevisionManager

SnapshotType = Tuple[Any, ...]


class DatabaseHistoryManager(ContainerHistoryManager):
    """Manage the history of a number of items in a database."""

    _temporary_database: Dict[EntryKeyType, EntryType]
    _history_database: Dict[EntryKeyType, RevisionManager]

    DoesNotExistError = EntryDoesNotExist
    LoadError = EntryLoadError

    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()
        # this is the database that entries will be directly edited in
        self._temporary_database: Dict[EntryKeyType, EntryType] = {}

        # this is the database where revisions will be cached
        self._history_database: Dict[EntryKeyType, RevisionManager] = {}

    def _check_snapshot(self, snapshot: SnapshotType):
        assert isinstance(snapshot, tuple)

    @property
    def changed(self) -> bool:
        """Have there been modifications since the last save."""
        if super().changed:
            return True
        try:
            next(self.changed_entries())
        except StopIteration:
            return False
        else:
            return True

    def changed_entries(self) -> Generator[EntryKeyType, None, None]:
        """A generator of all the entry keys that have changed since the last save."""
        changed = set()
        with self._lock:
            for key, entry in self._temporary_database.items():
                if entry is None:
                    # If the temporary entry is deleted but there was no historical
                    # record or the historical record was not deleted
                    if (
                        key not in self._history_database
                        or not self._history_database[key].is_deleted
                    ):
                        changed.add(key)
                        yield key

                elif entry.changed:
                    changed.add(key)
                    yield key
        for key, history_entry in self._history_database.items():
            if history_entry.changed and key not in changed:
                yield key

    def _all_entries(self, *args, **kwargs) -> Set[EntryKeyType]:
        with self._lock:
            keys = set()
            deleted_keys = set()
            for key in self._temporary_database.keys():
                if self._temporary_database[key] is None:
                    deleted_keys.add(key)
                else:
                    keys.add(key)

            for key in self._history_database.keys():
                if key not in self._temporary_database:
                    if self._history_database[key].is_deleted:
                        deleted_keys.add(key)
                    else:
                        keys.add(key)

            for key in self._raw_all_entries(*args, **kwargs):
                if key not in keys and key not in deleted_keys:
                    keys.add(key)

        return keys

    @abstractmethod
    def _raw_all_entries(self, *args, **kwargs) -> Iterable[EntryKeyType]:
        """
        The keys for all entries in the raw database.
        """
        raise NotImplementedError

    def __contains__(self, item: EntryKeyType) -> bool:
        return self._has_entry(item)

    def _has_entry(self, key: EntryKeyType):
        """
        Does the entry exist in one of the databases.
        Subclasses should implement a proper method calling this.
        """
        with self._lock:
            if key in self._temporary_database:
                return self._temporary_database[key] is not None
            elif key in self._history_database:
                return not self._history_database[key].is_deleted
            else:
                return self._raw_has_entry(key)

    @abstractmethod
    def _raw_has_entry(self, key: EntryKeyType) -> bool:
        """
        Does the raw database have this entry.
        Will be called if the key is not present in the loaded database.
        """
        raise NotImplementedError

    def _get_entry(self, key: EntryKeyType) -> Changeable:
        """
        Get a key from the database.
        Subclasses should implement a proper method calling this.
        """
        with self._lock:
            if key in self._temporary_database:
                # if the entry is loaded in RAM, just return it.
                entry = self._temporary_database[key]
            elif key in self._history_database:
                # if it is present in the cache, load it and return it.
                entry = self._temporary_database[key] = self._history_database[
                    key
                ].get_current_entry()
            else:
                # If it has not been loaded request it from the raw database.
                entry = self._temporary_database[
                    key
                ] = self._get_register_original_entry(key)
        if entry is None:
            raise self.DoesNotExistError
        return entry

    def _get_register_original_entry(self, key: EntryKeyType) -> EntryType:
        """Get and register the original entry."""
        try:
            entry = self._raw_get_entry(key)
        except EntryDoesNotExist:
            entry = None
        self._register_original_entry(key, entry)
        return entry

    def _register_original_entry(self, key: EntryKeyType, entry: EntryType):
        if key in self._history_database:
            raise Exception(f"The entry for {key} has already been registered.")
        self._history_database[key] = self._create_new_revision_manager(key, entry)

    @abstractmethod
    def _raw_get_entry(self, key: EntryKeyType) -> EntryType:
        """
        Get the entry from the raw database.
        Will be called if the key is not present in the loaded database.
        """
        raise NotImplementedError

    @staticmethod
    def _create_new_revision_manager(
        key: EntryKeyType, original_entry: EntryType
    ) -> RevisionManager:
        """Create an RevisionManager as desired and populate it with the original entry."""
        return RAMRevisionManager(original_entry)

    def _put_entry(self, key: EntryKeyType, entry: EntryType):
        with self._lock:
            entry.changed = True
            self._temporary_database[key] = entry

    def _delete_entry(self, key: EntryKeyType):
        with self._lock:
            self._temporary_database[key] = None

    def create_undo_point_iter(self) -> Generator[float, None, bool]:
        """
        Find all entries in the temporary database that have changed since the last undo point and create a new undo point.

        :return: Was an undo point created. If there were no changes no snapshot will be created.
        """
        with self._lock:
            snapshot = []
            count = len(self._temporary_database)
            for index, (key, entry) in enumerate(
                tuple(self._temporary_database.items())
            ):
                if entry is None or entry.changed:
                    if key not in self._history_database:
                        # The entry was added without populating from the world
                        # populate the history with the original entry
                        self._get_register_original_entry(key)
                    history_entry = self._history_database[key]
                    if (entry is None and not history_entry.is_deleted) or (
                        entry is not None and entry.changed
                    ):
                        # if the entry has been modified since the last history version
                        history_entry.put_new_entry(entry)
                        snapshot.append(key)
                yield index / count

            self._temporary_database.clear()  # unload all the data from the temporary database
            # so that it is repopulated from the history database. This fixes the issue of entries
            # being modified without the `changed` flag being set to True.

        return self._register_snapshot(tuple(snapshot))

    def _mark_saved(self):
        """Let the class know that the current state has been saved."""
        for entry in self._history_database.values():
            entry.mark_saved()

    def _undo(self, snapshot: SnapshotType):
        """Undoes the last set of changes to the database"""
        with self._lock:
            for key in snapshot:
                self._history_database[key].undo()
                if key in self._temporary_database:
                    del self._temporary_database[key]

    def _redo(self, snapshot: SnapshotType):
        """Redoes the last set of changes to the database"""
        with self._lock:
            for key in snapshot:
                self._history_database[key].redo()
                if key in self._temporary_database:
                    del self._temporary_database[key]

    def restore_last_undo_point(self):
        """Restore the state of the database to what it was when :meth:`create_undo_point_iter` was last called."""
        with self._lock:
            self._temporary_database.clear()

    def unload(self, *args, **kwargs):
        """Unload the entries loaded in RAM."""
        with self._lock:
            self._temporary_database.clear()

    def unload_unchanged(self, *args, **kwargs):
        """Unload all entries from RAM that have not been marked as changed."""
        with self._lock:
            unchanged = []
            for key, chunk in self._temporary_database.items():
                if not chunk.changed:
                    unchanged.append(key)
            for key in unchanged:
                del self._temporary_database[key]

    def purge(self):
        """Unload all cached data. Effectively returns the class to its starting state."""
        with self._lock:
            super().purge()
            self._temporary_database.clear()
            self._history_database.clear()

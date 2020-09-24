from typing import List, Tuple, Any, Dict, Generator
from .data_types import EntryKeyType, EntryType
from .entry_manager import BaseEntryManager
from amulet.api.errors import EntryDoesNotExist, EntryLoadError


class Database:
    DoesNotExistError = EntryDoesNotExist
    LoadError = EntryLoadError

    def __init__(self):
        # this is the database that entries will be directly edited in
        self._temporary_database: Dict[EntryKeyType, EntryType] = {}

        # this is the database where revisions will be cached
        self._history_database: Dict[EntryKeyType, BaseEntryManager] = {}

        self._snapshots: List[Tuple[Any]] = []
        self._snapshot_index: int = -1

        # the snapshot that was saved or the save branches off from
        self._last_save_snapshot = -1
        self._branch_save_count = 0  # if the user saves, undoes and does a new operation a save branch will be lost
        # This is the number of changes on that branch

    @property
    def changed(self) -> bool:
        """Has any data been modified since the last save."""
        try:
            next(self.changed_entries())
        except StopIteration:
            return False
        else:
            return True

    def changed_entries(self) -> Generator[EntryKeyType, None, None]:
        """A generator of all the entry keys that have changed since the last save."""
        changed = set()
        for key, entry in self._temporary_database.items():
            if entry is None:
                # If the temporary entry is deleted but there was no historical
                # record or the historical record was not deleted
                if key not in self._history_database or not self._history_database[key].is_deleted:
                    changed.add(key)
                    yield key

            elif entry.changed:
                changed.add(key)
                yield key
        for key, history_entry in self._history_database.items():
            if history_entry.changed and key not in changed:
                yield key

    def _has_entry(self, key: EntryKeyType):
        """Does the entry exist in one of the databases.
        Subclasses should implement a proper method calling this."""
        return key in self._temporary_database or key in self._history_database

    def _get_entry(self, key: EntryKeyType) -> EntryType:
        """Get a key from the database.
        Subclasses should implement a proper method calling this."""
        if key in self._temporary_database:
            entry = self._temporary_database[key]
        elif key in self._history_database:
            entry = self._temporary_database[key] = self._history_database[key].get_current_entry()
        else:
            entry = self._temporary_database[key] = self._get_register_original_entry(key)
        if entry is None:
            raise self.DoesNotExistError
        return entry

    def _get_register_original_entry(self, key: EntryKeyType) -> EntryType:
        """Get and register the original entry."""
        if key in self._history_database:
            raise Exception(f"The entry for {key} has already been registered.")
        try:
            entry = self._get_entry_from_world(key)
        except EntryDoesNotExist:
            entry = None
        self._history_database[key] = self._create_new_entry_manager(entry)
        return entry

    def _get_entry_from_world(self, key: EntryKeyType) -> EntryType:
        """If the entry was not found in the database request it from the world."""
        raise NotImplementedError

    def _create_new_entry_manager(self, original_entry: EntryType) -> BaseEntryManager:
        """Create an EntryManager as desired and populate it with the original entry."""
        raise NotImplementedError

    def _put_entry(self, key: EntryKeyType, entry: EntryType):
        entry.changed = True
        self._temporary_database[key] = entry

    def _delete_entry(self, key: EntryKeyType):
        self._temporary_database[key] = None

    def create_undo_point(self) -> bool:
        """
        Find all entries in the temporary database that have changed since the last undo point and create a new undo point.
        :return: Was a snapshot created. If there were no changes no snapshot will be created.
        """
        snapshot = []
        for key, entry in tuple(self._temporary_database.items()):
            if entry is None or entry.changed:
                if key not in self._history_database:
                    # The entry was added without populating from the world
                    # populate the history with the original entry
                    self._get_register_original_entry(key)
                history_entry = self._history_database[key]
                if (entry is None and not history_entry.is_deleted) or \
                        (entry is not None and entry.changed):
                    # if the entry has been modified since the last history version
                    history_entry.put_new_entry(entry)
                    snapshot.append(key)

        self._temporary_database.clear()  # unload all the data from the temporary database
        # so that it is repopulated from the history database. This fixes the issue of entries
        # being modified without the `changed` flag being set to True.

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
            del self._snapshots[self._snapshot_index:]
            self._snapshots.append(tuple(snapshot))
            return True
        return False

    def mark_saved(self):
        """Notify the database that the state it is currently in is the same as is saved in the world."""
        self._last_save_snapshot = self._snapshot_index
        self._branch_save_count = 0
        for entry in self._history_database.values():
            entry.mark_saved()

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
        if self._snapshot_index > -1:
            snapshot = self._snapshots[self._snapshot_index]
            for key in snapshot:
                self._history_database[key].undo()
                if key in self._temporary_database:
                    del self._temporary_database[key]
            self._snapshot_index -= 1

    def redo(self):
        """Redoes the last set of changes to the database"""
        if self._snapshot_index < len(self._snapshots) - 1:
            snapshot = self._snapshots[self._snapshot_index + 1]
            for key in snapshot:
                self._history_database[key].redo()
                if key in self._temporary_database:
                    del self._temporary_database[key]
            self._snapshot_index += 1

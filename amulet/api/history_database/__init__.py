"""
local history manager
    key based storage
        When a piece of data is loaded from disk it needs to be stored as revision 0
        If a piece of data is deleted it should be stored as None to specify that the data has been deleted
        If a piece of data was created rather than loaded from disk the revision 0 should be populated as None
            to specify that the revision 0 did not exist and the data should be added as revision 1
        It needs to store the revision index that is current within the editor.
        It also needs to store the revision that is saved to disk so that we know what has changed compared to
            the current save state rather than the original save state.
        If the above two indexes do not match then the data has been changed compared to the saved version so it needs saving.
    global storage
        We need to store a list of pools of keys that have changed for each undo point.
        We also need to store the index of which pool is current. This will get changed when undoing/redoing to keep track.


    When the creation of an undo point is requested
        we should scan all of the objects and see if the `changed` flag has been set to `True`.
        If this is the case the data has been changed and we should create a backup of it.
            make sure to reset the `changed` flag to False for the cached version
        A new revision for each entry is created and the current revision index is incremented.
        A pool of keys that have changed should be created.
            When undoing this change we look at this pool to see what changed and undo each of those.
            The same applies when redoing
        Finally the `changed` flags for each of the entries should be changed to False so that the next
            undo point only catches what has changed since this undo point.
            The better solution here is to empty the temporary database and re-populate from the latest cache
                revision where the `changed` flag was already set to False. This also solves the issue where
                the data was modified but the `changed` flag was not set to True by the script.

global history manager
    would store each of the local history managers
    would be the entry
"""

from __future__ import annotations

from abc import abstractmethod
from typing import List, Dict, Optional, TypeVar, Generic, Any

from copy import deepcopy

from contextlib import contextmanager

import random

T = TypeVar('T')


class TapeSection(Generic[T]):
    __slots__ = ("data", "prev_section", "next_section", "id")

    def __init__(
            self,
            data: T = None,
            previous_section: Optional[TapeSection] = None,
            next_section: Optional[TapeSection] = None,
            _id=None,
    ):
        self.data = data
        self.prev_section = previous_section
        self.next_section = next_section
        self.id = random.randrange(0, 9999) if not _id else _id

    def __repr__(self):
        return f"TapeSection(data={self.data}, previous={self.prev_section.id if self.prev_section else None}, next={self.next_section.id if self.next_section else None}, id={self.id})"

    @property
    def has_next(self):
        return self.next_section is not None

    @property
    def has_previous(self):
        return self.prev_section is not None

    def __del__(self):
        _next = self.next_section
        self.next_section = None
        del self.next_section
        del self.prev_section
        del _next
        del self.data
        del self.id


class TickerTape(Generic[T]):
    __slots__ = ("_current",)

    def __init__(self):
        self._current: Optional[TapeSection[T]] = None

    def __repr__(self):
        if self._current is None:
            return "TickerTape()"

        buffer = ""
        temp = self._current
        while temp is not None:
            buffer = f"{repr(temp)}, {buffer}"
            temp = temp.prev_section
        buffer += f"<{repr(self._current)}>"
        temp = self._current
        while temp is not None:
            buffer += f"{repr(temp)},"
            temp = temp.next_section
        return f"TickerTape({buffer})"

    def __len__(self):
        def helper(section: TapeSection, progress_func):
            new_section = progress_func(section)
            if new_section is None:
                return 0
            return 1 + helper(new_section, progress_func)

        return 1 + helper(self._current, lambda s: s.prev_section) + helper(self._current, lambda s: s.next_section)

    @property
    def current(self) -> T:
        return self._current.data

    def add(self, data: T):
        if self._current is None:
            self._current = TapeSection(data)
            return
        if self._current.has_next:
            _next = self._current.next_section
            self._current.next_section = None
            _next.prev_section = None
            del _next
        ts = TapeSection(data, previous_section=self._current)
        self._current.next_section = ts
        self._current = ts

    @property
    def has_next(self) -> bool:
        return self._current.has_next

    @property
    def has_previous(self) -> bool:
        return self._current.has_previous

    def move_back(self) -> T:
        if self._current is None:
            raise Exception("Cannot move back from a section that doesn't exist")
        if not self._current.has_previous:
            raise Exception("Current section has no previous section")
        self._current = self._current.prev_section
        return self._current.data

    def move_forward(self) -> T:
        if self._current is None:
            raise Exception("Cannot move forward from a section that doesn't exist")
        if not self._current.has_next:
            raise Exception("Current section has no next section")
        self._current = self._current.next_section
        return self._current.data


class HistoryManager:
    def __init__(self):
        self._in_transaction = False
        self._transactions: TickerTape[Dict[str, Any]] = TickerTape()
        self._in_original_state = True
        self.sub_managers: List[SubHistoryManager] = []

    @property
    def in_transaction(self) -> bool:
        return self._in_transaction

    def register(self, child_manager):
        if child_manager in self.sub_managers:
            raise Exception(
                f'Submanager "{child_manager.id}" has already been registered'
            )
        self.sub_managers.append(child_manager)

    def start_transaction(self):
        if self._in_transaction:
            raise Exception(
                "A new transaction cannot be started while a pre-existing transaction is active"
            )
        self._in_transaction = True
        for child in self.sub_managers:
            child.start_transaction()

    def end_transaction(self):
        if not self._in_transaction:
            raise Exception(
                "A transaction cannot be ended when there is no transaction active"
            )

        transaction = {}
        for child in self.sub_managers:
            transaction[child.id] = child.end_transaction()

        self._transactions.add(transaction)
        self._in_transaction = False
        self._in_original_state = False

    @contextmanager
    def transaction(self):
        self.start_transaction()
        yield
        self.end_transaction()

    def undo(self):
        if not self._transactions.has_previous:
            self._in_original_state = True
            for submngr in self.sub_managers:
                submngr.restore_originals()
            return

        transaction = self._transactions.move_back()
        for submngr in self.sub_managers:
            submngr.restore(transaction[submngr.id])

    def redo(self):
        if not self._transactions.has_next and not self._in_original_state:
            raise Exception

        if self._in_original_state:
            transaction = self._transactions.current
        else:
            transaction = self._transactions.move_forward()
        for submngr in self.sub_managers:
            submngr.restore(transaction[submngr.id])


class SubHistoryManager:
    def __init__(self, parent_history_manager: HistoryManager):
        self.history_manager = parent_history_manager
        parent_history_manager.register(self)
        self.retrieved_data = []

    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_data(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def restore(self, restored_data):
        raise NotImplementedError

    @abstractmethod
    def restore_originals(self):
        pass

    def start_transaction(self):
        pass

    def end_transaction(self):
        changed_data = []
        for data in self.retrieved_data:
            if data.changed:
                changed_data.append(data)
        return changed_data


class FakeChunkHistoryManager(SubHistoryManager):
    def __init__(self, parent):
        super(FakeChunkHistoryManager, self).__init__(parent)
        self.data_map = {}
        self.original_data = {}

    @property
    def id(self) -> str:
        return "fake_chunk_history_manager"

    def get_data(self, *args, **kwargs):
        in_transaction = self.history_manager.in_transaction
        if args[0] in self.data_map:
            data = (
                deepcopy(self.data_map[args[0]])
                if in_transaction
                else self.data_map[args[0]]
            )
        else:
            self.data_map[args[0]] = data = FakeChunk(args[0])
            self.original_data[args[0]] = deepcopy(data)

        if in_transaction:
            self.retrieved_data.append((deepcopy(data), data))
        return data

    def restore(self, restored_data):
        for data in restored_data:
            self.data_map[data.chunk_coords] = data

    def restore_originals(self):
        for key, data in self.original_data.items():
            self.data_map[key] = data

    def end_transaction(self):
        changed_data = []
        for original_state, current_state in self.retrieved_data:
            if current_state.changed:
                current_state.changed = False
                changed_data.append(current_state)
                self.data_map[current_state.chunk_coords] = current_state
        del self.retrieved_data
        self.retrieved_data = []
        return changed_data


class FakeChunk:
    def __init__(self, chunk_coords):
        self.chunk_coords = chunk_coords
        self.data = 0
        self.changed = False

    def __repr__(self):
        return f"FakeChunk({self.chunk_coords}, {self.data})"


if __name__ == "__main__":
    hm = HistoryManager()
    fchm = FakeChunkHistoryManager(hm)

    hm.start_transaction()
    obj = fchm.get_data((0, 0))
    print(obj)
    obj.data += 1
    obj.changed = True
    print(obj)
    print(obj.changed)
    hm.end_transaction()
    print("New State: ", fchm.get_data((0, 0)))
    hm.undo()
    print("Undone/Original State: ", fchm.get_data((0, 0)))
    hm.redo()
    print("Redone State: ", fchm.get_data((0, 0)))
    hm.undo()
    hm.redo()
    print("Redone State: ", fchm.get_data((0, 0)))

    print()
    hm.start_transaction()
    obj = fchm.get_data((0, 0))
    obj.data += 1
    obj.changed = True
    hm.end_transaction()
    print("Changed State: ", fchm.get_data((0, 0)))
    hm.undo()
    print("Undone State: ", fchm.get_data((0, 0)))
    print("(1,1): ", fchm.get_data((1, 1)))
    print()

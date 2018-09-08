from typing import List

from api.data_structures import SimpleStack
from api.operation import Operation


class HistoryManager:
    def __init__(self):
        self.undo_stack: List[Operation] = []
        self.redo_stack: SimpleStack[Operation] = SimpleStack()

    def add_operation(self, operation_instance: Operation):
        self.undo_stack.append(operation_instance)

    def undo(self):
        self.redo_stack.append(self.undo_stack.pop())

    def redo(self):
        self.undo_stack.append(self.redo_stack.pop())

    def __iter__(self):
        return iter(self.undo_stack)

    def __contains__(self, item):
        if isinstance(item, Operation):
            return item in self.undo_stack

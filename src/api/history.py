from __future__ import annotations

from api.data_structures import Stack
from api.operation import Operation


class HistoryManager:
    def __init__(self):
        self.undo_stack: Stack[Operation] = Stack()
        self.redo_stack: Stack[Operation] = Stack()

    def add_operation(self, operation_instance: Operation):
        self.undo_stack.append(operation_instance)

    def undo(self) -> Operation:
        operation_to_undo = self.undo_stack.pop()
        self.redo_stack.append(operation_to_undo)
        return operation_to_undo

    def redo(self) -> Operation:
        operation_to_redo = self.redo_stack.pop()
        self.undo_stack.append(operation_to_redo)
        return operation_to_redo

    def __contains__(self, item):
        if isinstance(item, Operation):
            return item in self.undo_stack

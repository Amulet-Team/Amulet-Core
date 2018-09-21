from __future__ import annotations

from typing import Sequence, Callable, TypeVar, Generic, Optional

T = TypeVar("T")


class Stack(Generic[T]):
    """
    Implementation of a Stack, but prevents out-of-order editing of stored data
    """

    def __init__(self, initial_data: Sequence[T] = None):
        self._data = initial_data or []
        self.__contains__ = self._data.__contains__
        self.pop: Callable[[], T] = self._data.pop
        self.append: Callable[[T], None] = self._data.append
        self.size: Callable[[], int] = self._data.__len__

    def peek(self) -> Optional[T]:
        """
        Returns the top element of the Stack without removing it

        :return: The top element of the Stack, None if the Stack is empty
        """
        if self.is_empty():
            return None

        return self._data[-1]

    def is_empty(self) -> bool:
        """
        Checks if the Stack is empty

        :return: True is the Stack holds elements, False otherwise
        """
        return len(self._data) == 0

    def clear(self):
        """
        Clears all stored elements in the Stack
        """
        self._data.clear()

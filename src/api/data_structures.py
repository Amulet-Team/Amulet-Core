from __future__ import annotations

import copy
from collections import UserDict
from contextlib import AbstractContextManager
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


class EntityContext(AbstractContextManager):
    def __init__(self, entities):
        self._entities = entities
        self._old_entities = copy.deepcopy(entities)

    def __enter__(self):
        return self._entities

    def __exit__(self, exc_type, exc_value, traceback):
        if self._entities != self._old_entities:
            print("Entities changed!")
        else:
            print("Nothing changed!")
        return False


class EntityDict(UserDict):
    def dict_iter(self):
        return super(EntityDict, self).__iter__()

    def __iter__(self):
        for coords, entities in self.data.items():
            yield from iter(entities)

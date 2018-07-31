from typing import Union, Sequence, Callable, TypeVar, Generic

T = TypeVar("T")


class SimpleStack(Generic[T]):

    def __init__(self, initial_data: Sequence[T] = None):
        if initial_data:
            self._data = initial_data
        else:
            self._data = []
        self.__contains__ = self._data.__contains__
        self.__len__ = self._data.__len__
        self.pop: Callable[[], T] = self._data.pop
        self.append: Callable[[T], None] = self._data.append

    def peek(self) -> Union[T, None]:
        if self.is_empty():
            return None

        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def clear(self):
        self._data.clear()

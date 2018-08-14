from typing import Generator, Sequence, Callable, TypeVar, Generic, Optional

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

    def peek(self) -> Optional[T]:
        if self.is_empty():
            return None

        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def clear(self):
        self._data.clear()


class LinkedStack(Generic[T]):

    class LinkedStackNode:

        def __init__(
            self,
            data: T,
            head: "LinkedStack.LinkedStackNode" = None,
            tail: "LinkedStack.LinkedStackNode" = None,
        ):
            self.data = data
            self.head = head
            self.tail = tail

    def __init__(self, initial_data: Sequence[T] = None):
        self._head_node: "LinkedStack.LinkedStackNode" = None
        self._tail_node: "LinkedStack.LinkedStackNode" = None
        self._length = 0
        if initial_data:
            map(self.append, initial_data)

    def append(self, data: T):
        self._length += 1
        if not self._head_node:
            self._head_node = self._tail_node = LinkedStack.LinkedStackNode(data)
            return

        node = LinkedStack.LinkedStackNode(data, self._tail_node)
        self._tail_node.tail = node
        self._tail_node = node

    def iter_forward(self) -> Generator[T, None, None]:
        current = self._head_node
        while current:
            yield current.data

            current = current.tail

    def iter_backward(self) -> Generator[T, None, None]:
        current = self._tail_node
        while current:
            yield current.data

            current = current.head

    def pop(self) -> Optional[T]:
        if not self._length:
            return None

        node = self._tail_node
        self._tail_node = node.head
        self._tail_node.tail = None
        return node.data

    def __str__(self):
        return f"[{', '.join(self.iter_forward())}]"

    def __len__(self):
        return self._length


if __name__ == "__main__":
    ls: LinkedStack[str] = LinkedStack()
    ls.append("test1")
    ls.append("test2")
    ls.append("test3")
    print(ls, len(ls))
    print(f"[{', '.join(ls.iter_backward())}]")
    print(ls.pop())
    print(ls, len(ls))

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


class Delegate:

    def __init__(self, initial_func: Callable = None):
        self._funcs = []
        self._arg_count = -1
        if initial_func:
            self._funcs.append(initial_func)
            self._arg_count = initial_func.__code__.co_argcount

    def __call__(self, *args, **kwargs):
        if len(self._funcs) == 0:
            return None

        result = self._funcs[0](*args, **kwargs)
        for func in self._funcs[1:]:
            func(*args, **kwargs)
        return result

    def __iadd__(self, other: Callable):
        if 0 <= self._arg_count != other.__code__.co_argcount:
            raise TypeError("Delegated functions must have the same amount of arguments as original function")
        elif self._arg_count == -1 and len(self._funcs) == 0:
            self._arg_count = other.__code__.co_argcount
        self._funcs.append(other)
        return self

    def __isub__(self, other: Callable):
        if other in self._funcs:
            self._funcs.remove(other)
        return self

@Delegate
def test_func(x, y, z, offset = None):
    print("Test")
    print(x,y,z)

def other_func(x,y,z, offset=None):
    print("other")
    print(z,y,x)

if __name__ == "__main__":
    """
    ls: LinkedStack[str] = LinkedStack()
    ls.append("test1")
    ls.append("test2")
    ls.append("test3")
    print(ls, len(ls))
    print(f"[{', '.join(ls.iter_backward())}]")
    print(ls.pop())
    print(ls, len(ls))
    """

    test_func(0,1,2)
    print("===")
    test_func += other_func
    test_func(0,1,2)
    print("===")
    test_func -= other_func
    test_func(0,1,2)

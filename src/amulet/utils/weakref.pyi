from typing import Any, Callable, Generic, TypeVar
from weakref import WeakMethod as _WeakMethod

T = TypeVar("T")

class CallableWeakMethod(_WeakMethod):
    """
    A wrapper around WeakMethod that makes the method directly callable.
    If the method no longer exists, this does nothing.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

class DetachableWeakRef(Generic[T]):
    """A weak reference that can be detached by the creator before the object is deleted."""

    @classmethod
    def new(cls, obj: T) -> tuple[DetachableWeakRef[T], Callable[[], None]]:
        """Get a new weak reference and a callable to detach the object.
        Once called the reference will always return None.
        """

    def __init__(self, obj: T) -> None: ...
    def __call__(self) -> T | None: ...

from typing import TypeVar, Any

T = TypeVar("T")


def dynamic_cast(obj: Any, cls: type[T]) -> T:
    """Like typing.cast but with runtime type checking."""
    if isinstance(obj, cls):
        return obj
    raise TypeError(f"{obj} is not an instance of {cls}")

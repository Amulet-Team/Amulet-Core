"""Extension to the builtin weakref module."""

from __future__ import annotations
from typing import Any, TypeVar, Generic, Callable, final
from weakref import WeakMethod as _WeakMethod, ReferenceType as _ReferenceType

T = TypeVar("T")


# Classes have an __del__ method to run code at object destruction.
# This is usually sufficient if the object gets deleted before the interpreter exits.
# In some cases global variables are set to None causing the __del__ to fail if run after interpreter shutdown.
# I have noticed this while debugging.
#
# In the following example when debugging sys is None when __del__ is called after interpreter shutdown.
#
# >>> import sys
# >>>
# >>> class Cls:
# >>>     def __init__(self) -> None:
# >>>         self._sys_modules = sys.modules
# >>>         print(self._sys_modules)
# >>>
# >>>     def __del__(self) -> None:
# >>>         print(self._sys_modules)
# >>>         print(sys)
# >>>
# >>> t = Cls()
#
# weakref.finalize takes care of this. It can be manually called in the __del__ method if the object is garbage
# collected before interpreter shutdown or automatically run at interpreter exit. It can only be called once.
# It must be given a weak method otherwise the instance will be kept alive until interpreter exit.
# weakref.WeakMethod is not directly callable so CallableWeakMethod is implemented to allow this.


@final
class CallableWeakMethod(_WeakMethod):
    """
    A wrapper around WeakMethod that makes the method directly callable.
    If the method no longer exists, this does nothing.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        meth = super().__call__()
        if meth is not None:
            return meth(*args, **kwargs)


@final
class DetachableWeakRef(Generic[T]):
    """A weak reference that can be detached by the creator before the object is deleted."""

    _ref: Callable[[], T | None]

    @classmethod
    def new(cls, obj: T) -> tuple[DetachableWeakRef[T], Callable[[], None]]:
        """Get a new weak reference and a callable to detach the object.
        Once called the reference will always return None.
        """
        self = cls(obj)
        return self, self._detach

    def __init__(self, obj: T) -> None:
        self._ref = _ReferenceType(obj)

    def __call__(self) -> T | None:
        return self._ref()

    def _detach(self) -> None:
        self._ref = lambda: None

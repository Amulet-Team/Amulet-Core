"""
Extension to the builtin weakref module.
"""

from __future__ import annotations
import typing
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import final
import weakref
from weakref import ReferenceType as _ReferenceType
from weakref import WeakMethod as _WeakMethod

__all__ = [
    "Any",
    "CallableWeakMethod",
    "DetachableWeakRef",
    "Generic",
    "T",
    "TypeVar",
    "final",
]

class CallableWeakMethod(weakref.WeakMethod):
    """

    A wrapper around WeakMethod that makes the method directly callable.
    If the method no longer exists, this does nothing.

    """

    __final__: typing.ClassVar[bool] = True
    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any: ...

class DetachableWeakRef(typing.Generic):
    """
    A weak reference that can be detached by the creator before the object is deleted.
    """

    __final__: typing.ClassVar[bool] = True
    @classmethod
    def new(cls, obj: T) -> tuple[DetachableWeakRef[T], typing.Callable[[], None]]:
        """
        Get a new weak reference and a callable to detach the object.
                Once called the reference will always return None.

        """

    def __call__(self) -> T | None: ...
    def __init__(self, obj: T) -> None: ...
    def _detach(self) -> None: ...

T: typing.TypeVar  # value = ~T

"""This modules contains classes to notify other code of the call specification for a function.
The aim is to support generating GUIs without having to manually program a GUI to handle the function call.
"""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    Hashable,
    Protocol,
    TypeVar,
    cast,
    ParamSpec,
    overload,
    Concatenate,
    runtime_checkable,
)
from abc import ABC, abstractmethod


class AbstractArg(ABC):
    """The base class for all arguments."""

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError


class AbstractHashableArg(AbstractArg, ABC):
    """A base class for all arguments that are hashable."""

    pass


class ConstantArg(AbstractArg):
    """A constant argument.
    Use this for fixed values.
    """

    def __init__(self, value: Any) -> None:
        self.value = value


class StringArg(AbstractHashableArg):
    """A string argument"""

    def __init__(self, default: str = "") -> None:
        self.default = default


class BytesArg(AbstractHashableArg):
    """A bytes argument"""

    def __init__(self, default: bytes = b"") -> None:
        self.default = default


class BoolArg(AbstractHashableArg):
    """A bool argument"""

    def __init__(self, default: bool = False) -> None:
        self.default = default


class IntArg(AbstractHashableArg):
    """An int argument"""

    def __init__(
        self,
        default: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> None:
        self.default = default
        self.min_value = min_value
        self.max_value = max_value


class FloatArg(AbstractHashableArg):
    """A float argument"""

    def __init__(
        self,
        default: float = 0,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> None:
        self.default = default
        self.min_value = min_value
        self.max_value = max_value


class TupleArg(AbstractArg):
    """A tuple argument"""

    def __init__(self, *args: AbstractArg) -> None:
        self.args = args


class HashableTupleArg(AbstractArg):
    """A tuple argument where all elements are hashable."""

    def __init__(self, *args: AbstractHashableArg) -> None:
        self.args = args


class ListArg(AbstractArg):
    """
    A sequence of other arguments.
    Each element must match element_type.
    length must be a positive integer for a fixed length or None for unbounded length.
    """

    def __init__(
        self,
        element_type: AbstractArg,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        self.element_type = element_type
        self.min_length = min_length
        self.max_length = max_length


class DictArg(AbstractArg):
    """A dictionary argument"""

    def __init__(self, key: AbstractHashableArg, value: AbstractArg) -> None:
        self.key = key
        self.value = value


class UnionArg(AbstractArg):
    """The object must match one of the types in args"""

    def __init__(self, *args: AbstractArg) -> None:
        self.args = args


class HashableUnionArg(AbstractArg):
    """The object must match one of the types in args"""

    def __init__(self, *args: AbstractHashableArg) -> None:
        self.args = args


class CallableArg(AbstractArg):
    """An argument generated by a function.
    This can be used to create instances of classes.
    kwargs specify the arguments to pass to the function.
    """

    def __init__(self, func: Callable[..., Any], call_spec: CallSpec) -> None:
        self.func = func
        self.call_spec = call_spec


class HashableCallableArg(AbstractHashableArg):
    """An argument generated by a function.
    This can be used to create instances of classes.
    kwargs specify the arguments to pass to the function.
    """

    def __init__(self, func: Callable[..., Hashable], call_spec: CallSpec) -> None:
        self.func = func
        self.call_spec = call_spec


class CallSpec:
    """Arguments and keyword arguments that should be unpacked to call a function."""

    def __init__(self, *args: AbstractArg, **kwargs: AbstractArg) -> None:
        self.args = args
        self.kwargs = kwargs


# The following is a really janky workaround to add a variable to a function or method in a way that mypy likes.
# This would be made so much simpler if Python had an Intersection type hint.

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


@runtime_checkable
class TypedCallable(Protocol[P, R]):
    call_spec: CallSpec

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...


@runtime_checkable
class TypedMethod(Protocol[P, R]):
    call_spec: CallSpec

    def __call__(self, self_: Any, *args: P.args, **kwargs: P.kwargs) -> R: ...

    @overload
    def __get__(self, instance: None, owner: None) -> TypedMethod[P, R]: ...

    @overload
    def __get__(self, instance: object, owner: object) -> TypedCallable[P, R]: ...


def callable_spec(
    call_spec: CallSpec,
) -> Callable[[Callable[P, R]], TypedCallable[P, R]]:
    def wrap(func: Callable[P, R]) -> TypedCallable[P, R]:
        func_ = cast(TypedCallable[P, R], func)
        func_.call_spec = call_spec
        return func_

    return wrap


def method_spec(
    call_spec: CallSpec,
) -> Callable[[Callable[Concatenate[Any, P], R]], TypedMethod[P, R]]:
    def wrap(func: Callable[Concatenate[Any, P], R]) -> TypedMethod[P, R]:
        func_ = cast(TypedMethod[P, R], func)
        func_.call_spec = call_spec
        return func_

    return wrap

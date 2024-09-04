"""
This modules contains classes to notify other code of the call specification for a function.
The aim is to support generating GUIs without having to manually program a GUI to handle the function call.
"""

from __future__ import annotations
import abc
from abc import ABC
from abc import abstractmethod
from collections.abc import Sequence
import typing
from typing import Any
from typing import ParamSpec
from typing import Protocol
from typing import TypeVar
from typing import cast
from typing import overload
from typing import runtime_checkable

__all__ = [
    "ABC",
    "AbstractArg",
    "AbstractHashableArg",
    "Any",
    "BoolArg",
    "BytesArg",
    "CallSpec",
    "CallableArg",
    "ConstantArg",
    "DictArg",
    "DirectoryPathArg",
    "DocumentationArg",
    "FilePathArg",
    "FloatArg",
    "HashableCallableArg",
    "HashableTupleArg",
    "HashableUnionArg",
    "IntArg",
    "P",
    "ParamSpec",
    "PositionalArgs",
    "Protocol",
    "R",
    "Sequence",
    "SequenceArg",
    "StringArg",
    "TupleArg",
    "TypeVar",
    "TypedCallable",
    "TypedMethod",
    "UnionArg",
    "abstractmethod",
    "callable_spec",
    "cast",
    "method_spec",
    "overload",
    "runtime_checkable",
]

class AbstractArg(abc.ABC):
    """
    The base class for all arguments.
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None: ...

class AbstractHashableArg(AbstractArg, abc.ABC):
    """
    A base class for all arguments that are hashable.
    """

class BoolArg(AbstractHashableArg):
    """
    A bool argument
    """

    def __init__(self, default: bool = False) -> None: ...

class BytesArg(AbstractHashableArg):
    """
    A bytes argument
    """

    def __init__(self, default: bytes = ...) -> None: ...

class CallSpec:
    """
    Arguments and keyword arguments that should be unpacked to call a function.
    """

    def __init__(self, *args: AbstractArg, **kwargs: AbstractArg) -> None: ...

class CallableArg(AbstractArg):
    """
    An argument generated by a function.
        This can be used to create instances of classes.
        kwargs specify the arguments to pass to the function.

    """

    def __init__(
        self,
        func: typing.Callable[..., typing.Any],
        *args: AbstractArg,
        **kwargs: AbstractArg,
    ) -> None: ...

class ConstantArg(AbstractArg):
    """
    A constant argument.
        Use this for fixed values.

    """

    def __init__(self, value: typing.Any) -> None: ...

class DictArg(AbstractArg):
    """
    A dictionary argument
    """

    def __init__(self, key: AbstractHashableArg, value: AbstractArg) -> None: ...

class DirectoryPathArg(StringArg):
    """
    A path to a directory on disk. Converts to a string.
    """

class DocumentationArg(AbstractArg):
    """
    A way to add documentation for an argument.
    """

    def __init__(
        self, arg: AbstractArg, name: str | None = None, description: str | None = None
    ) -> None:
        """
        Construct a DocumentationArg instance.

                :param arg: The argument this documentation relates to.
                :param name: The short name for the argument.
                :param description: A longer description for the argument.

        """

class FilePathArg(StringArg):
    """
    A path to a file on disk. Converts to a string.
    """

class FloatArg(AbstractHashableArg):
    """
    A float argument
    """

    def __init__(
        self,
        default: float = 0,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> None: ...

class HashableCallableArg(AbstractHashableArg):
    """
    An argument generated by a function.
        This can be used to create instances of classes.
        kwargs specify the arguments to pass to the function.

    """

    def __init__(
        self, func: typing.Callable[..., Hashable], call_spec: CallSpec
    ) -> None: ...

class HashableTupleArg(AbstractArg):
    """
    A tuple argument where all elements are hashable.
    """

    def __init__(self, *args: AbstractHashableArg) -> None: ...

class HashableUnionArg(AbstractArg):
    """
    The object must match one of the types in args
    """

    def __init__(self, *args: AbstractHashableArg) -> None: ...

class IntArg(AbstractHashableArg):
    """
    An int argument
    """

    def __init__(
        self,
        default: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> None: ...

class PositionalArgs(SequenceArg):
    """
    A sequence of arguments that should be unpacked into the container.
        This is useful when a CallableArg can take a variable number of an argument.

    """

class SequenceArg(AbstractArg):
    """

    A sequence of other arguments.
    Each element must match element_type.
    length must be a positive integer for a fixed length or None for unbounded length.

    """

    def __init__(
        self,
        element_type: AbstractArg,
        default: typing.Sequence[AbstractArg] = tuple(),
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None: ...

class StringArg(AbstractHashableArg):
    """
    A string argument
    """

    def __init__(self, default: str = "") -> None: ...

class TupleArg(AbstractArg):
    """
    A tuple argument
    """

    def __init__(self, *args: AbstractArg) -> None: ...

class TypedCallable(typing.Protocol):
    __non_callable_proto_members__: typing.ClassVar[set] = {"call_spec"}
    _is_runtime_protocol: typing.ClassVar[bool] = True
    @classmethod
    def __subclasshook__(cls, other): ...
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def __init__(self, *args, **kwargs): ...

class TypedMethod(typing.Protocol):
    __non_callable_proto_members__: typing.ClassVar[set] = {"call_spec"}
    _is_runtime_protocol: typing.ClassVar[bool] = True
    @staticmethod
    def __get__(*args, **kwds):
        """
        Helper for @overload to raise when called.
        """

    @classmethod
    def __subclasshook__(cls, other): ...
    def __call__(self, self_: typing.Any, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def __init__(self, *args, **kwargs): ...

class UnionArg(AbstractArg):
    """
    The object must match one of the types in args
    """

    def __init__(self, *args: AbstractArg) -> None: ...

def callable_spec(
    *args: AbstractArg, **kwargs: AbstractArg
) -> typing.Callable[[typing.Callable[P, R]], TypedCallable[P, R]]: ...
def method_spec(
    *args: AbstractArg, **kwargs: AbstractArg
) -> typing.Callable[
    [typing.Callable[Concatenate[typing.Any, P], R]], TypedMethod[P, R]
]: ...

P: typing.ParamSpec  # value = ~P
R: typing.TypeVar  # value = +R

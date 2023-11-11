import abc
from ._level import Level as Level
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

class StringArg:
    """A string argument"""
    default: Incomplete
    def __init__(self, default: str = ...) -> None: ...

class BytesArg:
    """A bytes argument"""
    default: Incomplete
    def __init__(self, default: bytes = ...) -> None: ...

class BoolArg:
    """A bool argument"""
    default: Incomplete
    def __init__(self, default: bool = ...) -> None: ...

class IntArg:
    """An int argument"""
    default: Incomplete
    min_value: Incomplete
    max_value: Incomplete
    def __init__(self, default: int = ..., min_value: Optional[int] = ..., max_value: Optional[int] = ...) -> None: ...

class FloatArg:
    """A float argument"""
    default: Incomplete
    min_value: Incomplete
    max_value: Incomplete
    def __init__(self, default: float = ..., min_value: Optional[float] = ..., max_value: Optional[float] = ...) -> None: ...

class SequenceArg:
    """
    A sequence of other arguments.
    Each element must match element_type
    """
    element_type: Incomplete
    length: Incomplete
    def __init__(self, element_type: CreateArgsT, length: Optional[int] = ...) -> None: ...

class UnionArg:
    """The object must match one of the types in args"""
    args: Incomplete
    def __init__(self, *args: CreateArgsT) -> None: ...

class ProtocolArg:
    """The object must have attributes matching those defined in kwargs"""
    kwargs: Incomplete
    def __init__(self, **kwargs: CreateArgsT) -> None: ...
CreateArgsT = Union[StringArg, BytesArg, BoolArg, IntArg, FloatArg, SequenceArg, UnionArg, ProtocolArg]

class CreatableLevel(ABC, metaclass=abc.ABCMeta):
    """Level extension class for levels that can be created without data."""
    __slots__: Incomplete
    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> Union[Level, CreatableLevel]:
        """
        Create a new instance without any existing data.
        You must call :meth:`~amulet.level.BaseLevel.open` to open the level for editing.
        :return: A new BaseLevel instance
        """
    @staticmethod
    @abstractmethod
    def create_args() -> dict[str, CreateArgsT]:
        """The arguments required to create a new instance of this level."""

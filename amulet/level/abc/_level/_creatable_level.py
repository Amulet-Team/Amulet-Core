from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from ._level import Level


# The following classes are used to notify a GUI of the types required to create a new instance of the level.
# This means that the GUI does not need to be aware of the class to create a new instance of it.


class StringArg:
    """A string argument"""

    def __init__(self, default: str = "") -> None:
        self.default = default


class BytesArg:
    """A bytes argument"""

    def __init__(self, default: bytes = b"") -> None:
        self.default = default


class BoolArg:
    """A bool argument"""

    def __init__(self, default: bool = False) -> None:
        self.default = default


class IntArg:
    """An int argument"""

    def __init__(
        self,
        default: int = 0,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> None:
        self.default = default
        self.min_value = min_value
        self.max_value = max_value


class FloatArg:
    """A float argument"""

    def __init__(
        self,
        default: float = 0,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> None:
        self.default = default
        self.min_value = min_value
        self.max_value = max_value


class SequenceArg:
    """
    A sequence of other arguments.
    Each element must match element_type
    """

    def __init__(self, element_type: CreateArgsT, length: Optional[int] = None) -> None:
        self.element_type = element_type
        self.length = length


class UnionArg:
    """The object must match one of the types in args"""

    def __init__(self, *args: CreateArgsT) -> None:
        self.args = args


class ProtocolArg:
    """The object must have attributes matching those defined in kwargs"""

    def __init__(self, **kwargs: CreateArgsT) -> None:
        self.kwargs = kwargs


CreateArgsT = Union[
    StringArg, BytesArg, BoolArg, IntArg, FloatArg, SequenceArg, UnionArg, ProtocolArg
]


class CreatableLevel(ABC):
    """Level extension class for levels that can be created without data."""

    __slots__ = ()

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> Union[Level, CreatableLevel]:
        """
        Create a new instance without any existing data.
        You must call :meth:`~amulet.level.BaseLevel.open` to open the level for editing.
        :return: A new BaseLevel instance
        """
        # If writing data to disk, it must write a valid level.
        # If only setting attributes, the open method must be aware that it should not load data from disk.
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create_args() -> dict[str, CreateArgsT]:
        """The arguments required to create a new instance of this level."""
        raise NotImplementedError

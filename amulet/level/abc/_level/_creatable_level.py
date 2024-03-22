from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from amulet.utils.typing import Intersection
from ._call_spec import method_spec, CallSpec


if TYPE_CHECKING:
    from ._level import Level


class CreatableLevel(ABC):
    """Level extension class for levels that can be created without data."""

    __slots__ = ()

    @classmethod
    @abstractmethod
    @method_spec(CallSpec())
    def create(cls, *args: Any, **kwargs: Any) -> Intersection[Level, CreatableLevel]:
        """
        Create a new instance without any existing data.
        You must call :meth:`~amulet.level.BaseLevel.open` to open the level for editing.
        :return: A new BaseLevel instance
        """
        # If writing data to disk, it must write a valid level.
        # If only setting attributes, the open method must be aware that it should not load data from disk.
        raise NotImplementedError

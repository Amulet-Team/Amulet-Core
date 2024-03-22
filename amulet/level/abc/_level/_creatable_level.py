from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from amulet.utils.typing import Intersection


if TYPE_CHECKING:
    from ._level import Level


class CreatableLevel(ABC):
    """Level extension class for levels that can be created without data."""

    __slots__ = ()

    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> Intersection[Level, CreatableLevel]:
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

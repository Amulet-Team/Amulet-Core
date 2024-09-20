import abc
from abc import ABC, abstractmethod
from typing import Any

from amulet.utils.call_spec import method_spec as method_spec
from amulet.utils.typing import Intersection as Intersection

from ._level import Level as Level

class CreatableLevel(ABC, metaclass=abc.ABCMeta):
    """Level extension class for levels that can be created without data."""

    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> Intersection[Level, CreatableLevel]:
        """
        Create a new instance without any existing data.
        You must call :meth:`~amulet.level.abc.Level.open` to open the level for editing.
        :return: A new Level instance
        """

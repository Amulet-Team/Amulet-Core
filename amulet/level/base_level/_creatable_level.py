from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, TYPE_CHECKING


if TYPE_CHECKING:
    from ._base_level import BaseLevel


class CreatableLevel(ABC):
    """Level extension class for levels that can be created without data."""

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> Union[BaseLevel, CreatableLevel]:
        """
        Create a new instance without any existing data.
        If writing data to disk it must write a valid level.
        If only setting attributes, the open method must be aware that it should not load data from disk.
        :return: A new BaseLevel instance
        """
        raise NotImplementedError

import abc
from ._level import Level as Level
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from typing import Any, Union

class LoadableLevel(ABC, metaclass=abc.ABCMeta):
    """Level extension class for levels that can be loaded from existing data."""
    __slots__: Incomplete
    @staticmethod
    @abstractmethod
    def can_load(token: Any) -> bool:
        """
        Returns whether this level class is able to load the given data.

        :param token: The token to check. Usually a file or directory path.
        :return: True if the level can be loaded by this format wrapper, False otherwise.
        """
    @classmethod
    @abstractmethod
    def load(cls, token: Any) -> Union[Level, LoadableLevel]:
        """
        Create a new instance from existing data.
        You must call :meth:`~amulet.level.BaseLevel.open` to open the level for editing.
        :param token: The token to use to load the data.
        :return: A new BaseLevel instance
        """
    @abstractmethod
    def reload(self) -> None:
        """
        Reload the metadata in the existing instance.
        This can only be done when the level is not open.
        """

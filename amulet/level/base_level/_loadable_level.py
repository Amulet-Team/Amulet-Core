from __future__ import annotations

from typing import Any, Union
from abc import ABC, abstractmethod

from ._base_level import BaseLevel


class LoadableLevel(ABC):
    """Level extension class for levels that can be loaded from existing data."""

    @staticmethod
    @abstractmethod
    def can_load(token: Any) -> bool:
        """
        Returns whether this level class is able to load the given data.

        :param token: The token to check. Usually a file or directory path.
        :return: True if the level can be loaded by this format wrapper, False otherwise.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def load(cls, token: Any) -> Union[BaseLevel, LoadableLevel]:
        """
        Create a new instance from existing data.
        You must call :meth:`~amulet.level.BaseLevel.open` to open the level for editing.
        :param token: The token to use to load the data.
        :return: A new BaseLevel instance
        """
        raise NotImplementedError

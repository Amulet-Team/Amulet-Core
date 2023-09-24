from __future__ import annotations

from typing import Any, Union
from abc import ABC, abstractmethod

from ._base_level import BaseLevel


class LoadableLevel(ABC):
    """Level extension class for levels that can be loaded from existing data."""

    @classmethod
    @abstractmethod
    def load(cls, token: Any) -> Union[BaseLevel, LoadableLevel]:
        """
        Create a new instance from existing data.
        :param token: The token to use to load the data.
        :return: A new BaseLevel instance
        """
        raise NotImplementedError

from __future__ import annotations

from abc import ABC, abstractmethod
from .namespace import LevelNamespace


class ReadonlyMetadataNamespace(LevelNamespace, ABC):
    """
    Read-only metadata about the level.
    Everything here can be used when the level is open or closed.
    """

    @abstractmethod
    def level_name(self) -> str:
        """The human-readable name of the level"""
        raise NotImplementedError

    @property
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """
        return 16

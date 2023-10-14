from __future__ import annotations

from typing import Any

from amulet.level.base_level import (
    DiskLevel,
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
)
from ._level_dat import BedrockLevelDAT


class BedrockLevel(DiskLevel, CreatableLevel, LoadableLevel, CompactableLevel):
    _path: str
    _dat: BedrockLevelDAT

    __slots__ = tuple(__annotations__)

    @classmethod
    def create(cls, *args, **kwargs) -> BedrockLevel:
        raise NotImplementedError

    @classmethod
    def load(cls, token: Any) -> BedrockLevel:
        raise NotImplementedError

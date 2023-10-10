from __future__ import annotations

from typing import Any

from amulet.level.base_level import (
    DiskLevel,
    CreatableLevel,
    LoadableLevel,
    CompactableLevel,
)


class BedrockLevel(DiskLevel, CreatableLevel, LoadableLevel, CompactableLevel):
    __slots__ = ()

    @classmethod
    def create(cls, *args, **kwargs) -> BedrockLevel:
        raise NotImplementedError

    @classmethod
    def load(cls, token: Any) -> BedrockLevel:
        raise NotImplementedError

from __future__ import annotations

from typing import Any

from amulet.level.base_level import DiskLevel, CreatableLevel, LoadableLevel


class BedrockLevel(DiskLevel, CreatableLevel, LoadableLevel):
    @classmethod
    def create(cls, *args, **kwargs) -> BedrockLevel:
        raise NotImplementedError

    @classmethod
    def load(cls, token: Any) -> BedrockLevel:
        raise NotImplementedError

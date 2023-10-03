from __future__ import annotations

from typing import Any

from amulet.level.base_level import DiskLevel, CreatableLevel, LoadableLevel


class JavaLevel(DiskLevel, CreatableLevel, LoadableLevel):
    @classmethod
    def create(cls, *args, **kwargs) -> JavaLevel:
        raise NotImplementedError

    @classmethod
    def load(cls, token: Any) -> JavaLevel:
        raise NotImplementedError

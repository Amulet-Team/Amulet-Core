from __future__ import annotations

from typing import Any
from amulet.level.abc import Level, CreatableLevel
from amulet.utils.call_spec import method_spec


class TemporaryLevel(Level, CreatableLevel):
    """A temporary level that exists only in memory."""

    __slots__ = ()

    @classmethod
    @method_spec()
    def create(cls, *args: Any, **kwargs: Any) -> TemporaryLevel:
        raise NotImplementedError

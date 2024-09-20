import abc
from typing import Any

from amulet.level.abc import CreatableLevel as CreatableLevel
from amulet.level.abc import Level as Level
from amulet.utils.call_spec import method_spec as method_spec

class TemporaryLevel(Level, CreatableLevel, metaclass=abc.ABCMeta):
    """A temporary level that exists only in memory."""

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> TemporaryLevel: ...

import abc
from _typeshed import Incomplete
from amulet.level.abc import CreatableLevel as CreatableLevel, Level as Level

class TemporaryLevel(Level, CreatableLevel, metaclass=abc.ABCMeta):
    """A temporary level that exists only in memory."""
    __slots__: Incomplete
    @classmethod
    def create(cls) -> TemporaryLevel: ...

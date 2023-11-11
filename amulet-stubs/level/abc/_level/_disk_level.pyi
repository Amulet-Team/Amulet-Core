import abc
from ._level import Level as Level, LevelPrivateT as LevelPrivateT, RawLevelT as RawLevelT
from _typeshed import Incomplete
from abc import abstractmethod

class DiskLevel(Level[LevelPrivateT, RawLevelT], metaclass=abc.ABCMeta):
    """A level base class for all levels with data on disk."""
    __slots__: Incomplete
    @property
    @abstractmethod
    def path(self) -> str:
        """The path to the level on disk."""

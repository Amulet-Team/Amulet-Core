import abc
from ._level import DimensionT as DimensionT, Level as Level, LevelPrivateT as LevelPrivateT, RawLevelT as RawLevelT
from _typeshed import Incomplete
from abc import abstractmethod
from amulet.version import VersionT as VersionT

class DiskLevel(Level[LevelPrivateT, DimensionT, VersionT, RawLevelT], metaclass=abc.ABCMeta):
    """A level base class for all levels with data on disk."""
    __slots__: Incomplete
    @property
    @abstractmethod
    def path(self) -> str:
        """The path to the level on disk."""

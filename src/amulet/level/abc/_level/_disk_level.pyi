import abc
from abc import abstractmethod

from ._level import DimensionT as DimensionT
from ._level import Level as Level
from ._level import OpenLevelDataT as OpenLevelDataT
from ._level import RawLevelT as RawLevelT

class DiskLevel(Level[OpenLevelDataT, DimensionT, RawLevelT], metaclass=abc.ABCMeta):
    """A level base class for all levels with data on disk."""

    @property
    @abstractmethod
    def path(self) -> str:
        """The path to the level on disk."""

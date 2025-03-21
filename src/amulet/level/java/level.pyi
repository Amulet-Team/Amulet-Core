from __future__ import annotations

import amulet.level.abc.level
import amulet.level.java.dimension
import amulet.level.java.raw_level

__all__ = ["JavaLevel"]

class JavaLevel(
    amulet.level.abc.level.Level,
    amulet.level.abc.level.CompactibleLevel,
    amulet.level.abc.level.DiskLevel,
    amulet.level.abc.level.ReloadableLevel,
):
    @staticmethod
    def create(args: amulet.level.java.raw_level.JavaCreateArgsV1) -> JavaLevel:
        """
        Create a new Java level at the given directory.
        Thread safe.
        """

    @staticmethod
    def load(path: str) -> JavaLevel:
        """
        Load an existing Java level from the given directory.
        Thread safe.
        """

    def get_dimension(
        self, dimension_id: str
    ) -> amulet.level.java.dimension.JavaDimension:
        """
        Get a dimension.
        External Read:SharedReadWrite lock required.
        External ReadWrite:SharedReadWrite lock required when calling code in Dimension (and its children) that need write permission.
        """

    @property
    def raw_level(self) -> amulet.level.java.raw_level.JavaRawLevel:
        """
        Access the raw level instance.
        Before calling any mutating functions, the caller must call :meth:`purge` (optionally saving before)
        External ReadWrite:Unique lock required.
        """

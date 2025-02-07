from __future__ import annotations

import datetime

import amulet.level.abc.registry
import amulet.level.java.raw_dimension
import amulet.utils.lock
import amulet.version
import amulet_nbt

__all__ = ["JavaCreateArgsV1", "JavaRawLevel"]

class JavaCreateArgsV1:
    def __init__(
        self,
        overwrite: bool,
        path: str,
        version: amulet.version.VersionNumber,
        level_name: str,
    ) -> None: ...
    @property
    def level_name(self) -> str: ...
    @property
    def overwrite(self) -> bool: ...
    @property
    def path(self) -> str: ...
    @property
    def version(self) -> amulet.version.VersionNumber: ...

class JavaRawLevel:
    @staticmethod
    def create(args: JavaCreateArgsV1) -> JavaRawLevel:
        """
        Create a new Java level at the given directory.
        Thread safe.
        """

    @staticmethod
    def load(path: str) -> JavaRawLevel:
        """
        Load an existing Java level from the given directory.
        Thread safe.
        """

    def close(self) -> None:
        """
        Close the level.
        External unique lock required.
        """

    def compact(self) -> None:
        """
        Compact the level.
        External shared read lock required.
        """

    def get_biome_id_override(self) -> amulet.level.abc.registry.IdRegistry:
        """
        Overridden biome ids.
        External shared read lock required.
        """

    def get_block_id_override(self) -> amulet.level.abc.registry.IdRegistry:
        """
        Overridden block ids.
        External shared read lock required.
        """

    def get_dimension(
        self, dimension_id: str
    ) -> amulet.level.java.raw_dimension.JavaRawDimension:
        """
        Get the raw dimension object for a specific dimension.
        External shared read lock required.
        """

    def is_open(self) -> bool:
        """
        Is the level open.
        External shared read lock required.
        """

    def lock(self) -> amulet.utils.lock.OrderedLock:
        """
        The public lock
        Thread safe.
        """

    def open(self) -> None:
        """
        Open the level.
        External unique lock required.
        """

    def reload_metadata(self) -> None:
        """
        Reload the metadata. This can only be called when the level is closed.
        External unique lock required.
        """

    @property
    def data_version(self) -> amulet.version.VersionNumber:
        """
        Getter:
        The game data version that the level was last opened in.
        External shared read lock required.

        Setter:
        Set the maximum game version.
        If the game version is different this will close and re-open the level.
        External unique lock required.
        """

    @data_version.setter
    def data_version(self, arg1: amulet.version.VersionNumber) -> None: ...
    @property
    def dimension_ids(self) -> list[str]:
        """
        The identifiers for all dimensions in this level.
        External shared read lock required.
        External shared read-only lock optional.
        """

    @property
    def level_dat(self) -> amulet_nbt.NamedTag:
        """
        Getter:
        The NamedTag stored in the level.dat file. Returns a unique copy.
        External shared read lock required.

        Setter:
        Set the level.dat NamedTag
        External unique lock required.
        """

    @level_dat.setter
    def level_dat(self, arg1: amulet_nbt.NamedTag) -> None: ...
    @property
    def level_name(self) -> str:
        """
        Getter:
        The name of the level.
        External shared read lock required.

        Setter:
        Set the level name.
        External unique lock required.
        """

    @level_name.setter
    def level_name(self, arg1: str) -> None: ...
    @property
    def modified_time(self) -> datetime.datetime:
        """
        The time when the level was lasted edited.
        External shared read lock required.
        """

    @property
    def path(self) -> str:
        """
        The path to the level directory.
        Thread safe.
        """

    @property
    def platform(self) -> str:
        """
        The platform identifier. "java"
        Thread safe.
        """

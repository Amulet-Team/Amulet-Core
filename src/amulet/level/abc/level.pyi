from __future__ import annotations

import datetime

import amulet.level.abc.dimension
import amulet.utils.lock
import amulet.utils.signal
import amulet.version
import PIL.Image

__all__ = ["CompactibleLevel", "DiskLevel", "Level", "LevelMetadata", "ReloadableLevel"]

class CompactibleLevel:
    def compact(self) -> None:
        """
        Compact the level data to reduce file size.
        External unique lock required.
        """

class DiskLevel:
    def path(self) -> str:
        """
        The path to the level on disk.
        External shared read lock required.
        """

class Level(LevelMetadata):
    def close(self) -> None:
        """
        Close the level.

        If the level is not open, this does nothing.
        """

    def create_restore_point(self) -> None:
        """
        Create a new history restore point.
        Any changes made after this point can be reverted by calling undo.
        External shared lock required.
        """

    def dimension_ids(self) -> list[str]:
        """
        The identifiers for all dimensions in the level.
        External shared read lock required.
        """

    def get_dimension(self, dimension_id: str) -> amulet.level.abc.dimension.Dimension:
        """
        Get a dimension.
        External shared read lock required.
        """

    def get_redo_count(self) -> int:
        """
        Get the number of times redo can be called.
        External shared lock required.
        """

    def get_undo_count(self) -> int:
        """
        Get the number of times undo can be called.
        External shared lock required.
        """

    def open(self) -> None:
        """
        Open the level.

        If the level is already open, this does nothing.
        External unique lock required.
        """

    def purge(self) -> None:
        """
        Clear all unsaved changes and restore points.
        External unique lock required.
        """

    def redo(self) -> None:
        """
        Redo changes that were previously reverted.
        External unique lock required.
        """

    def save(self) -> None:
        """
        Save all changes to the level.
        External unique lock required.
        """

    def undo(self) -> None:
        """
        Revert the changes made since the previous restore point.
        External unique lock required.
        """

    @property
    def closed(self) -> amulet.utils.signal.Signal[()]:
        """
        Signal emitted when the level is closed.
        Thread safe.
        """

    @property
    def history_changed(self) -> amulet.utils.signal.Signal[()]:
        """
        A signal emitted when the undo or redo count changes.
        Thread safe.
        """

    @property
    def history_enabled(self) -> bool:
        """
        A boolean tracking if the history system is enabled.

        If true, the caller must call :meth:`create_restore_point` before making changes.
        :attr:`history_enabled_changed` is emitted when this is set.
        """

    @history_enabled.setter
    def history_enabled(self, arg1: bool) -> None: ...
    @property
    def history_enabled_changed(self) -> amulet.utils.signal.Signal[()]:
        """
        A signal emitted when set_history_enabled is called.
        Thread safe.
        """

    @property
    def opened(self) -> amulet.utils.signal.Signal[()]:
        """
        Signal emitted when the level is opened.
        Thread safe.
        """

    @property
    def purged(self) -> amulet.utils.signal.Signal[()]:
        """
        Signal emitted when the level is purged
        Thread safe.
        """

class LevelMetadata:
    def is_open(self) -> bool:
        """
        Has the level been opened.
        External shared read lock required.

        :return: True if the level is open otherwise False.
        """

    def is_supported(self) -> bool:
        """
        Is this level a supported version.
        This is true for all versions we support and false for snapshots, betas and unsupported newer versions.
        """

    @property
    def level_name(self) -> str:
        """
        The name of the level
        External shared read lock required.
        """

    @property
    def lock(self) -> amulet.utils.lock.OrderedLock:
        """
        The external mutex for the level.
        Thread safe.
        """

    @property
    def max_game_version(self) -> amulet.version.VersionNumber:
        """
        The maximum game version the level has been opened with.
        External shared read lock required.
        """

    @property
    def modified_time(self) -> datetime.datetime:
        """
        The time when the level was last modified.
        External shared read lock required.
        """

    @property
    def platform(self) -> str:
        """
        The platform string for the level.
        External shared read lock required.
        """

    @property
    def sub_chunk_size(self) -> int:
        """
        The size of the sub-chunk. Must be a cube.
        External shared read lock required.
        """

    @property
    def thumbnail(self) -> PIL.Image.Image:
        """
        The thumbnail for the level.
        External shared read lock required.
        """

class ReloadableLevel:
    def reload(self) -> None:
        """
        Reload the level.
        This is like closing and opening the level but does not release locks.
        This can only be done when the level is open.External unique mutex required.
        """

    def reload_metadata(self) -> None:
        """
        Reload the level metadata.
        This can only be done when the level is not open.
        External unique mutex required.
        """

    @property
    def reloaded(self) -> amulet.utils.signal.Signal[()]:
        """
        Signal emitted when the level is reloaded.
        Thread safe.
        """

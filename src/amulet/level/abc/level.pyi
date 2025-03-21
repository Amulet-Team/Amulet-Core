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
        External ReadWrite:SharedReadWrite lock required.
        """

class DiskLevel:
    @property
    def path(self) -> str:
        """
        The path to the level on disk.
        External Read:SharedReadWrite lock required.
        """

class Level(LevelMetadata):
    def close(self) -> None:
        """
        Close the level.
        External ReadWrite:Unique lock required.

        If the level is not open, this does nothing.
        """

    def create_restore_point(self) -> None:
        """
        Create a new history restore point.
        Any changes made after this point can be reverted by calling undo.
        External Read:SharedReadWrite lock required.
        """

    def dimension_ids(self) -> list[str]:
        """
        The identifiers for all dimensions in the level.
        External Read:SharedReadWrite lock required.
        External Read:SharedReadOnly lock optional.
        """

    def get_dimension(self, dimension_id: str) -> amulet.level.abc.dimension.Dimension:
        """
        Get a dimension.
        External Read:SharedReadWrite lock required.
        External ReadWrite:SharedReadWrite lock required when calling code in Dimension (and its children) that need write permission.
        """

    def get_redo_count(self) -> int:
        """
        Get the number of times redo can be called.
        External Read:SharedReadWrite lock required.
        External Read:SharedReadOnly lock optional.
        """

    def get_undo_count(self) -> int:
        """
        Get the number of times undo can be called.
        External Read:SharedReadWrite lock required.
        External Read:SharedReadOnly lock optional.
        """

    def open(self) -> None:
        """
        Open the level.

        If the level is already open, this does nothing.
        External ReadWrite:Unique lock required.
        """

    def purge(self) -> None:
        """
        Clear all unsaved changes and restore points.
        External ReadWrite:Unique lock required.
        """

    def redo(self) -> None:
        """
        Redo changes that were previously reverted.
        External ReadWrite:SharedReadWrite lock required.
        External ReadWrite:Unique lock optional.
        """

    def save(self) -> None:
        """
        Save all changes to the level.
        External ReadWrite:Unique lock required.
        """

    def undo(self) -> None:
        """
        Revert the changes made since the previous restore point.
        External ReadWrite:SharedReadWrite lock required.
        External ReadWrite:Unique lock optional.
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
        External Read:SharedReadWrite lock required when getting.
        External ReadWrite:SharedReadWrite lock required when setting.

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
        External Read:SharedReadWrite lock required.

        :return: True if the level is open otherwise False.
        """

    def is_supported(self) -> bool:
        """
        Is this level a supported version.
        This is true for all versions we support and false for snapshots, betas and unsupported newer versions.
        External Read:SharedReadWrite lock required.
        """

    @property
    def level_name(self) -> str:
        """
        The name of the level
        External Read:SharedReadWrite lock required.
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
        External Read:SharedReadWrite lock required.
        """

    @property
    def modified_time(self) -> datetime.datetime:
        """
        The time when the level was last modified.
        External Read:SharedReadWrite lock required.
        """

    @property
    def platform(self) -> str:
        """
        The platform string for the level.
        External Read:SharedReadWrite lock required.
        """

    @property
    def sub_chunk_size(self) -> int:
        """
        The size of the sub-chunk. Must be a cube.
        External Read:SharedReadWrite lock required.
        """

    @property
    def thumbnail(self) -> PIL.Image.Image:
        """
        The thumbnail for the level.
        External Read:SharedReadWrite lock required.
        """

class ReloadableLevel:
    def reload(self) -> None:
        """
        Reload the level.
        This is like closing and opening the level but does not release locks.
        This can only be done when the level is open.External ReadWrite:Unique lock required.
        """

    def reload_metadata(self) -> None:
        """
        Reload the level metadata.
        This can only be done when the level is not open.
        External ReadWrite:Unique lock required.
        """

    @property
    def reloaded(self) -> amulet.utils.signal.Signal[()]:
        """
        Signal emitted when the level is reloaded.
        Thread safe.
        """

from __future__ import annotations

import amulet.level.abc.dimension
import amulet.version

__all__ = ["CompactibleLevel", "DiskLevel", "Level", "LevelMetadata", "ReloadableLevel"]

class CompactibleLevel:
    def compact(self) -> None: ...

class DiskLevel:
    def path(self) -> str: ...

class Level(LevelMetadata):
    def close(self) -> None:
        """
        Close the level.

        If the level is not open, this does nothing.

        :param task_manager: The cancel manager through which cancel can be requested.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """

    def dimension_ids(self) -> list[str]: ...
    def get_dimension(
        self, dimension_id: str
    ) -> amulet.level.abc.dimension.Dimension: ...
    def open(self) -> None:
        """
        Open the level.

        If the level is already open, this does nothing.

        :param task_manager: The cancel manager through which cancel can be requested.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """

    def purge(self) -> None:
        """
        Unload all loaded data.
        This is a nuclear function and must be used with :meth:`lock_unique`

        This is functionally the same as closing and reopening the level.
        """

    def save(self) -> None:
        """
        Save all changes to the level
        """

class LevelMetadata:
    def is_open(self) -> bool:
        """
        Has the level been opened.

        :param task_manager: The cancel manager through which cancel can be requested.
        :return: True if the level is open otherwise False.
        :raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled.
        """

    @property
    def level_name(self) -> str:
        """
        The human-readable name of the level
        """

    @property
    def max_game_version(self) -> amulet.version.VersionNumber: ...
    @property
    def modified_time(self) -> float:
        """
        The unix float timestamp of when the level was last modified.
        """

    @property
    def platform(self) -> str: ...
    @property
    def sub_chunk_size(self) -> int:
        """
        The dimensions of a sub-chunk.
        """

class ReloadableLevel:
    def reload(self) -> None: ...

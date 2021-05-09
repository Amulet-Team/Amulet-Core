from abc import abstractmethod
from typing import Generator

from amulet.utils.generator import generator_unpacker

from .base_history import BaseHistory


class HistoryManager(BaseHistory):
    """The base class for all active history manager objects.
    The HistoryManager tracks which objects have changed but is not aware of how they have changed."""

    def create_undo_point(self) -> bool:
        """
        Find what has changed since the last undo point and optionally create a new undo point.

        :return: Was an undo point created. If there were no changes no snapshot will be created.
        """
        return generator_unpacker(self.create_undo_point_iter())

    @abstractmethod
    def create_undo_point_iter(self) -> Generator[float, None, bool]:
        """
        Find what has changed since the last undo point and optionally create a new undo point.

        :return: Was an undo point created. If there were no changes no snapshot will be created.
        """
        raise NotImplementedError

    @abstractmethod
    def restore_last_undo_point(self):
        """
        Restore the world to the state it was when self.create_undo_point was called.

        If an operation errors there may be modifications made that did not get tracked.

        This will revert those changes.
        """
        raise NotImplementedError

    @abstractmethod
    def purge(self):
        """Unload all cached data. Effectively returns the class to its starting state."""
        raise NotImplementedError

    @property
    @abstractmethod
    def undo_count(self) -> int:
        """The number of times the :meth:`undo` method can be run."""
        raise NotImplementedError

    @property
    @abstractmethod
    def redo_count(self) -> int:
        """The number of times the :meth:`redo` method can be run."""
        raise NotImplementedError

    @property
    @abstractmethod
    def unsaved_changes(self) -> int:
        """The number of changes that have been made since the last save"""
        raise NotImplementedError

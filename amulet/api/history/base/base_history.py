from abc import ABC, abstractmethod


class BaseHistory(ABC):
    """The base class for all history related objects"""

    @abstractmethod
    def undo(self):
        """Revert to the previous state."""
        raise NotImplementedError

    @abstractmethod
    def redo(self):
        """Un-revert to the next state."""
        raise NotImplementedError

    @abstractmethod
    def mark_saved(self):
        """Let the class know that the current state has been saved."""
        raise NotImplementedError

    @property
    @abstractmethod
    def changed(self) -> bool:
        """Have there been modifications since the last save."""
        raise NotImplementedError

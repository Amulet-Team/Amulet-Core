class BaseHistory:
    """The base class for all history related objects"""

    def undo(self):
        """Revert to the previous state."""
        raise NotImplementedError

    def redo(self):
        """Un-revert to the next state."""
        raise NotImplementedError

    def mark_saved(self):
        """Let the class know that the current state has been saved."""
        raise NotImplementedError

    @property
    def changed(self) -> bool:
        """Have there been modifications since the last save."""
        raise NotImplementedError

class Changeable:
    """A class to track if an object has been changed."""

    def __init__(self):
        self._changed = False

    @property
    def changed(self) -> bool:
        """Has the object been modified since the last revision."""
        return self._changed

    @changed.setter
    def changed(self, changed: bool):
        assert isinstance(changed, bool), "Changed must be a bool"
        self._changed = changed

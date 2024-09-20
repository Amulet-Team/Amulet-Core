from typing import Any

from _typeshed import Incomplete
from amulet.level.abc import LoadableLevel as LoadableLevel

log: Incomplete

def register_level_class(cls) -> None:
    """Add a level class to be considered when getting a level.

    :param cls: The Level subclass to register.
    :return:
    """

def unregister_level_class(cls) -> None:
    """Remove a level class from consideration when getting a level.

    Note that any instances of the class will remain.

    :param cls: The Level subclass to unregister.
    """

class NoValidLevel(Exception):
    """An error thrown if no level could load the token."""

def get_level(token: Any) -> LoadableLevel:
    """Get the level for the given token.

    If a level object already exists for this token then that will be returned.
    This will return a subclass of Level specialised for that level type.
    Note that the returned level may or may not be open.
    The level will automatically close itself when the last reference is lost so you must hold a strong reference to it.

    :param token: The token to load. This may be a file/directory path or some other token.
    :return: The level instance.
    :raises:
        NoValidLevel: If no level could load the token.

        Exception: Other errors.
    """

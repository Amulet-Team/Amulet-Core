from __future__ import annotations

from typing import Type, Any
import logging
from inspect import isclass
from threading import Lock
from weakref import WeakValueDictionary

from amulet.level.abc import LoadableLevel


log = logging.getLogger(__name__)


_level_classes = set[Type[LoadableLevel]]()
_levels = WeakValueDictionary[Any, LoadableLevel]()
_lock = Lock()


def _check_loadable_level(cls: Any) -> None:
    if not (isclass(cls) and issubclass(cls, LoadableLevel)):
        raise TypeError(
            "cls must be a subclass of amulet.level.abc.Level and amulet.level.abc.LoadableLevel"
        )


def register_level_class(cls: Type[LoadableLevel]) -> None:
    """Add a level class to be considered when getting a level.

    :param cls: The Level subclass to register.
    :return:
    """
    _check_loadable_level(cls)
    with _lock:
        _level_classes.add(cls)


def unregister_level_class(cls: Type[LoadableLevel]) -> None:
    """Remove a level class from consideration when getting a level.

    Note that any instances of the class will remain.

    :param cls: The Level subclass to unregister.
    """
    _check_loadable_level(cls)
    with _lock:
        _level_classes.discard(cls)


class NoValidLevel(Exception):
    """An error thrown if no level could load the token."""

    pass


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
    level: None | LoadableLevel
    with _lock:
        # Find the level to load the token
        cls = next((cls for cls in _level_classes if cls.can_load(token)), None)

        if cls is None:
            # If no level could load the token then raise
            raise NoValidLevel(f"Could not load {token}")

        try:
            # Try and get a cached instance of the level
            level = _levels.get(token)
            if level is not None:
                # If there is a cached instance then return it
                return level
        except TypeError:
            # If the token is not hashable
            pass

        # Load the level
        level = cls.load(token)

        try:
            # Cache the level
            _levels[token] = level
        except TypeError:
            # Token may not be hashable
            pass

        return level

from __future__ import annotations

from typing import Union
import logging

from amulet.api.level import World, Structure, BaseLevel

from amulet.api.wrapper import WorldFormatWrapper, StructureFormatWrapper
from . import loader

log = logging.getLogger(__name__)


def load_level(token) -> BaseLevel:
    """
    Load and return a :class:`World` or :class:`Structure` class exposing the data at ``path``

    Calls :func:`load_format` to try and find a :class:`FormatWrapper` that can open the data.

    If one is found it will wrap it with either a :class:`World` or :class:`Structure` class and return it.

    :param token: The token to load. This is usually a str path to the directory or file on disk.
    :return: A World or Structure class instance containing the data.
    :raises:
        LoaderNoneMatched: If no loader could be found that can open the data at path.

        Exception: Other errors.
    """
    log.info(f"Loading level {token}")
    format_wrapper = load_format(token)
    if isinstance(format_wrapper, WorldFormatWrapper):
        return World(token, format_wrapper)
    elif isinstance(format_wrapper, StructureFormatWrapper):
        return Structure(token, format_wrapper)
    else:
        raise Exception(
            f"FormatWrapper of type {format_wrapper.__class__.__name__} is not supported. Report this to a developer."
        )


def load_format(token) -> Union[WorldFormatWrapper, StructureFormatWrapper]:
    """
    Find a valid subclass of :class:`FormatWrapper` and return the data wrapped in the class.
    This exposes a low level API to read and write the world data.

    Inspects the data at the given path to find a valid subclass of :class:`FormatWrapper`.

    If a valid wrapper is found it is set up and returned.

    This is not recommended for new users and does not include a history system.

    :param token: The token to load. This is usually a str path to the directory or file on disk.
    :return: An instance of WorldFormatWrapper or StructureFormatWrapper containing the data at path.
    :raises:
        LoaderNoneMatched: If no loader could be found that can open the data at path.

        Exception: Other errors.
    """
    return loader.Formats.get(token).load(token)

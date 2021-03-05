from __future__ import annotations

from typing import Union

from amulet import log
from amulet.api.level import World, Structure

from amulet.api.wrapper import WorldFormatWrapper, StructureFormatWrapper
from . import loader


def load_level(path: str) -> Union[World, Structure]:
    """Creates a FormatWrapper loader from the given path and wraps it in a World or Structure class.
    :param path: The file path to a file or directory for the object to be loaded.
    :return: A World or Structure class instance containing the data.
    :raises:
        LoaderNoneMatched: If no loader could be found that can open the data at path.
        Exception: Other errors.
    """
    log.info(f"Loading level {path}")
    format_wrapper = load_format(path)
    if isinstance(format_wrapper, WorldFormatWrapper):
        return World(path, format_wrapper)
    elif isinstance(format_wrapper, StructureFormatWrapper):
        return Structure(path, format_wrapper)
    else:
        raise Exception(
            f"FormatWrapper of type {format_wrapper.__class__.__name__} is not supported. Report this to a developer."
        )


def load_format(path: str) -> Union[WorldFormatWrapper, StructureFormatWrapper]:
    """Loads the level located at the given path with the appropriate FormatWrapper.

    :param path: The file path to a file or directory for the object to be loaded.
    :return: An instance of WorldFormatWrapper or StructureFormatWrapper containing the data at path.
    :raises:
        LoaderNoneMatched: If no loader could be found that can open the data at path.
        Exception: Other errors.
    """
    return loader.Formats.get(path)(path)

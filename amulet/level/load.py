from __future__ import annotations

from typing import Union

from amulet import log
from amulet.api.level import World, Structure

from amulet.api.wrapper import WorldFormatWrapper, StructureFormatWrapper
from . import loader


def load_level(path: str) -> Union[World, Structure]:
    """
    Creates a Format loader from the given inputs and wraps it in a World class
    :param path:
    :return:
    """
    log.info(f"Loading level {path}")
    format_wrapper = load_format(path)
    if isinstance(format_wrapper, WorldFormatWrapper):
        return World(path, format_wrapper)
    elif isinstance(format_wrapper, StructureFormatWrapper):
        return Structure(path, format_wrapper)
    else:
        raise Exception


def load_format(path: str) -> Union[WorldFormatWrapper, StructureFormatWrapper]:
    """
    Loads the level located at the given path with the appropriate format loader.

    :param path: The path of the level
    :return: The loaded level
    """
    return loader.Formats.get(path)(path)

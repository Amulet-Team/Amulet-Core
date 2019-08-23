from __future__ import annotations

from typing import Tuple

from . import version_loader
from . import format_loader
from .world import World
from .errors import (
    FormatLoaderNoneMatched,
    FormatLoaderInvalidFormat,
    FormatLoaderMismatched,
    VersionLoaderInvalidFormat,
    VersionLoaderMismatched,
)


def identify(directory: str) -> Tuple[str, str]:
    """
    Identifies the level format the world is in and the versions definitions that match
    the world.

    Note: Since Minecraft Java versions below 1.12 lack version identifiers, they
    will always be loaded with 1.12 definitions and always be identified as "java_1_12"

    :param directory: The directory of the world
    :return: The version definitions name for the world and the format loader that would be used
    """
    for version_name in version_loader.get_all_versions():
        version_module, version_format = version_loader.get_version(version_name)

        if version_module.identify(directory):
            return version_name, version_format

    raise FormatLoaderNoneMatched("Could not find a matching format loader")


def load_world(
    directory: str, _format: str = None, _version: str = None, forced: bool = False
) -> World:
    """
    Loads the world located at the given directory with the appropriate version/format loader.

    :param directory: The directory of the world
    :param _format: The loader name to use
    :param _version: The version name to use
    :param forced: Whether to force load the world even if incompatible
    :return: The loaded world
    """
    if _format is not None:
        if _format not in format_loader.get_all_formats():
            raise FormatLoaderInvalidFormat(f"Could not find _format loader {_format}")
        if _version not in version_loader.get_all_versions():
            raise VersionLoaderInvalidFormat(f"Could not find _version {_version}")
        if not forced and not identify(directory)[1] == _format:
            raise FormatLoaderMismatched(f"{_format} is incompatible")
        if not forced and not identify(directory) == _version:
            raise VersionLoaderMismatched(f"{_version} is incompatible")
    else:
        _version, _format = identify(directory)

    format_module = format_loader.get_format(_format)
    version_module = version_loader.get_version(_version).module
    blockstate_adapter = getattr(version_module, "parse_blockstate", None)

    return format_module.LEVEL_CLASS.load(
        directory, _version, get_blockstate_adapter=blockstate_adapter
    )

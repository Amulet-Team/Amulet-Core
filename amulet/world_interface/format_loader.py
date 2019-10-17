from __future__ import annotations

import glob
import json
import os

from typing import Dict, AbstractSet
from importlib.util import spec_from_file_location, module_from_spec

from ..api.errors import FormatLoaderNoneMatched
from .formats.format import Format

SUPPORTED_FORMAT_VERSION = 0
SUPPORTED_META_VERSION = 0

_loaded_formats: Dict[str, Format] = {}
_has_loaded_formats = False

FORMATS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'formats')


def _find_formats():
    global _has_loaded_formats

    directories = glob.iglob(os.path.join(FORMATS_DIRECTORY, "*", ""))
    for d in directories:
        meta_path = os.path.join(d, "format.meta")
        if not os.path.exists(meta_path):
            continue

        with open(meta_path) as fp:
            format_info = json.load(fp)

        if format_info["meta_version"] != SUPPORTED_META_VERSION:
            print(
                f'[Error] Couldn\'t enable format located in "{d}" due to unsupported meta version'
            )
            continue

        if format_info["format"]["format_version"] != SUPPORTED_FORMAT_VERSION:
            print(
                f"[Error] Couldn't enable format \"{format_info['format']['id']}\" due to unsupported format version"
            )
            continue

        spec = spec_from_file_location(
            format_info["format"]["entry_point"],
            os.path.join(d, format_info["format"]["entry_point"] + ".py"),
        )

        modu = module_from_spec(spec)
        spec.loader.exec_module(modu)

        if not hasattr(modu, "FORMAT_CLASS"):
            print(
                f"[Error] Format \"{format_info['format']['id']}\" is missing the FORMAT_CLASS attribute"
            )
            continue

        _loaded_formats[format_info["format"]["id"]] = modu.FORMAT_CLASS

        if __debug__:
            print(
                f"[Debug] Enabled format \"{format_info['format']['id']}\", version {format_info['format']['wrapper_version']}"
            )

    _has_loaded_formats = True


def reload():
    """Reloads all formats"""
    _loaded_formats.clear()
    _find_formats()


def get_all_formats() -> AbstractSet[str]:
    """
    :return: The names of all loaded formats
    """
    if not _has_loaded_formats:
        _find_formats()
    return _loaded_formats.keys()


def get_format(format_id: str) -> Format:
    """
    Gets the module for the format with the given ``format_id``

    :param format_id: The id for the desired loaded format
    :return: The module object for the format
    """
    if not _has_loaded_formats:
        _find_formats()
    if format_id not in _loaded_formats:
        raise FormatLoaderNoneMatched("Could not find a matching format loader")
    return _loaded_formats[format_id]


def identify(directory: str) -> str:
    """
    Identifies the format the world is in.

    Note: Since Minecraft Java versions below 1.12 lack version identifiers, they
    will always be loaded with 1.12 definitions and always be identified as "java_1_12"

    :param directory: The directory of the world
    :return: The version definitions name for the world and the format loader that would be used
    """
    if not _has_loaded_formats:
        _find_formats()

    for format_name, format_class in _loaded_formats.items():
        if format_class.is_valid(directory):
            return format_name

    raise FormatLoaderNoneMatched("Could not find a matching format loader")


if __name__ == "__main__":
    import time

    _find_formats()
    print(_loaded_formats)
    time.sleep(1)
    reload()
    print(_loaded_formats)

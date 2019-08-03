from __future__ import annotations

from . import format_loader
from ..api.world import World
from ..api.errors import (
    FormatLoaderInvalidFormat,
    FormatLoaderMismatched,
)

def load_world(directory: str, _format: str = None, forced: bool = False) -> World:
    """
    Loads the world located at the given directory with the appropriate format loader.

    :param directory: The directory of the world
    :param _format: The format name to use
    :param forced: Whether to force load the world even if incompatible
    :return: The loaded world
    """
    if _format is not None:
        if _format not in format_loader.get_all_formats():
            raise FormatLoaderInvalidFormat(f"Could not find _format loader {_format}")
        if not forced and not format_loader.identify(directory) == _format:
            raise FormatLoaderMismatched(f"{_format} is incompatible")
    else:
        _format = format_loader.identify(directory)

    format_class = format_loader.get_format(_format)

    return format_class(directory)

if __name__ == '__main__':
    import sys
    w = load_world(sys.argv[1])
    c = w.get_chunk(0, 0)
    print(c.blocks[0,60,0])

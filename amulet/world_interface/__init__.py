from __future__ import annotations

import os
from typing import TYPE_CHECKING

from amulet import log
from amulet.world_interface import formats
from amulet.api.world import World
from amulet.api.errors import FormatLoaderInvalidFormat, FormatLoaderMismatched

if TYPE_CHECKING:
    from amulet.api.wrapper.world_format_wrapper import WorldFormatWrapper


def load_world(directory: str, _format: str = None, forced: bool = False) -> World:
    """
    Creates a Format loader from the given inputs and wraps it in a World class
    :param directory:
    :param _format:
    :param forced:
    :return:
    """
    log.info(f"Loading world {directory}")
    return World(directory, load_format(directory, _format, forced))


def load_format(
    directory: str, _format: str = None, forced: bool = False
) -> "WorldFormatWrapper":
    """
    Loads the world located at the given directory with the appropriate format loader.

    :param directory: The directory of the world
    :param _format: The format name to use
    :param forced: Whether to force load the world even if incompatible
    :return: The loaded world
    """
    if not os.path.isdir(directory):
        if os.path.exists(directory):
            log.error(f'The path "{directory}" does exist but it is not a directory')
            raise Exception(
                f'The path "{directory}" does exist but it is not a directory'
            )
        else:
            log.error(
                f'The path "{directory}" is not a valid path on this file system.'
            )
            raise Exception(
                f'The path "{directory}" is not a valid path on this file system.'
            )
    if _format is not None:
        if _format not in formats.loader:
            log.error(f"Could not find _format loader {_format}")
            raise FormatLoaderInvalidFormat(f"Could not find _format loader {_format}")
        if not forced and not formats.loader.identify(directory) == _format:
            log.error(f"{_format} is incompatible")
            raise FormatLoaderMismatched(f"{_format} is incompatible")
        format_class = formats.loader.get_by_id(_format)
    else:
        format_class = formats.loader.get(directory)
    return format_class(directory)


if __name__ == "__main__":
    import sys
    from amulet.api.block import Block
    import numpy

    cx, cz = 0, 0

    w = load_world(sys.argv[1])
    c = w.get_chunk(cx, cz, "overworld")
    for block in c.blocks[0, :, 0].ravel():  # the blockstates of one vertical column
        print(w.palette[block])
    air = w.palette.get_add_block(
        Block(namespace="universal_minecraft", base_name="air")
    )
    # blocks[0, 30, 0] = stone
    blocks = numpy.random.randint(0, len(w.palette.blocks()), size=(16, 256, 16))
    for index, block in enumerate(w.palette.blocks()):
        if block.base_name in ["lava", "water"]:
            blocks[blocks == index] = air
    c.blocks[:, :, :] = blocks
    w.save()
    w.close()

    w = load_world(sys.argv[1])
    c = w.get_chunk(cx, cz, "overworld")
    for block in c.blocks[0, :, 0].ravel():  # the blockstates of one vertical column
        print(w.palette[block])

from __future__ import annotations

from amulet.world_interface import formats
from amulet.api.world import World
from amulet.api.errors import FormatLoaderInvalidFormat, FormatLoaderMismatched


def load_world(directory: str, _format: str = None, forced: bool = False) -> World:
    """
    Loads the world located at the given directory with the appropriate format loader.

    :param directory: The directory of the world
    :param _format: The format name to use
    :param forced: Whether to force load the world even if incompatible
    :return: The loaded world
    """
    if _format is not None:
        if _format not in formats.loader.get_all():
            raise FormatLoaderInvalidFormat(f"Could not find _format loader {_format}")
        if not forced and not formats.loader.identify(directory) == _format:
            raise FormatLoaderMismatched(f"{_format} is incompatible")
        format_class: formats.Format = formats.loader.get_by_id(_format)
    else:
        format_class: formats.Format = formats.loader.get(directory)
    return World(directory, format_class(directory))


if __name__ == "__main__":
    import sys
    from amulet.api.block import Block
    import numpy
    cx, cz = 0, 0

    w = load_world(sys.argv[1])
    c = w.get_chunk(cx, cz)
    for block in c.blocks.ravel()[:4096:16]:    # the blockstates of one vertical column
        print(w.palette[block])
    air = w.palette.get_add_block(Block(namespace='universal_minecraft', base_name='air'))
    # blocks[0, 30, 0] = stone
    # c.blocks = numpy.full((16, 256, 16), stone)
    blocks = numpy.random.randint(0, len(w.palette.blocks()), size=(16, 256, 16))
    for index, block in enumerate(w.palette.blocks()):
        if block.base_name in ['lava', 'water']:
            blocks[blocks == index] = air
    c.blocks = blocks
    w.save()
    w.exit()

    w = load_world(sys.argv[1])
    c = w.get_chunk(cx, cz)
    for block in c.blocks.ravel()[:4096:16]:  # the blockstates of one vertical column
        print(w.palette[block])

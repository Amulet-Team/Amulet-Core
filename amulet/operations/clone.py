from amulet.api.selection import SelectionGroup
from amulet.api.data_types import Dimension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.world import ChunkWorld


def clone(
    world: "ChunkWorld", dimension: Dimension, selection: SelectionGroup, target: dict
):
    dst_location = (target.get("x", 0), target.get("y", 0), target.get("z", 0))
    world.paste(world, dimension, selection, dimension, dst_location)

from amulet.api.selection import SelectionGroup
from amulet.api.data_types import Dimension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel


def clone(
    world: "BaseLevel", dimension: Dimension, selection: SelectionGroup, target: dict
):
    offset_x, offset_y, offset_z = (selection.max_array - selection.min_array) // 2
    dst_location = (
        target.get("x", 0) + offset_x,
        target.get("y", 0) + offset_y,
        target.get("z", 0) + offset_y,
    )
    world.paste(world, dimension, selection, dimension, dst_location)

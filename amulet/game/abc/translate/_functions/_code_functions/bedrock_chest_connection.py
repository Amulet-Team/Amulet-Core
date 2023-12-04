from typing import Callable
from amulet_nbt import CompoundTag, IntTag, ByteTag, StringTag
from .._state import SrcData, StateData, DstData


def _bedrock_chest_connection(connections: dict[tuple[int, int, int], StringTag]) -> Callable[[SrcData, StateData, DstData], None]:
    def main(src: SrcData, state: StateData, dst: DstData) -> None:
        nbt = src.nbt
        if nbt is None:
            return

        tag = nbt.tag
        if not isinstance(tag, CompoundTag):
            return

        if tag.get("pairlead") != ByteTag(1):
            return

        pairx = tag.get("pairx")
        if not isinstance(pairx, IntTag):
            return

        pairz = tag.get("pairz")
        if not isinstance(pairz, IntTag):
            return

        block = src.block
        if block is None:
            return
        extra = src.extra
        if extra is None:
            dst.extra_needed = True
            return

        facing_direction = block.properties.get("facing_direction")
        if not isinstance(facing_direction, IntTag):
            return

        dx = pairx.py_int - extra.absolute_coordinates[0]
        dz = pairz.py_int - extra.absolute_coordinates[2]

        connection = connections.get((facing_direction.py_int, dx, dz))
        if connection is None:
            return
        dst.properties["connection"] = connection
    return main


bedrock_chest_connection_other_left = _bedrock_chest_connection({
    (2, -1, 0): StringTag("left"),  # north
    (3, 1, 0): StringTag("left"),  # south
    (4, 0, 1): StringTag("left"),  # west
    (5, 0, -1): StringTag("left"),  # east
})

bedrock_chest_connection_other_right = _bedrock_chest_connection({
    (2, 1, 0): StringTag("right"),  # north
    (3, -1, 0): StringTag("right"),  # south
    (4, 0, -1): StringTag("right"),  # west
    (5, 0, 1): StringTag("right"),  # east
})

bedrock_chest_connection_self = _bedrock_chest_connection({
    (2, -1, 0): StringTag("right"),  # north
    (2, 1, 0): StringTag("left"),  # north
    (3, 1, 0): StringTag("right"),  # south
    (3, -1, 0): StringTag("left"),  # south
    (4, 0, 1): StringTag("right"),  # west
    (4, 0, -1): StringTag("left"),  # west
    (5, 0, -1): StringTag("right"),  # east
    (5, 0, 1): StringTag("left"),  # east
})

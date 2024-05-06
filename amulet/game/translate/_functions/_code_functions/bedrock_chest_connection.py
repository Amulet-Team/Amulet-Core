from typing import Callable, Any
from amulet_nbt import CompoundTag, IntTag, ByteTag, StringTag, AbstractBaseTag
from .._state import SrcData, StateData, DstData


def _bedrock_chest_connection(
    facing_property: str, connections: dict[tuple[Any, int, int], StringTag]
) -> Callable[[SrcData, StateData, DstData], None]:
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

        facing_direction = block.properties.get(facing_property)
        if not isinstance(facing_direction, AbstractBaseTag):
            return

        dx = pairx.py_int - extra.absolute_coordinates[0]
        dz = pairz.py_int - extra.absolute_coordinates[2]

        connection = connections.get((facing_direction.py_data, dx, dz))
        if connection is None:
            return
        dst.properties["connection"] = connection

    return main


bedrock_chest_connection_other_left = _bedrock_chest_connection(
    "facing_direction",
    {
        (2, -1, 0): StringTag("left"),  # north
        (3, 1, 0): StringTag("left"),  # south
        (4, 0, 1): StringTag("left"),  # west
        (5, 0, -1): StringTag("left"),  # east
    },
)

bedrock_chest_connection_other_right = _bedrock_chest_connection(
    "facing_direction",
    {
        (2, 1, 0): StringTag("right"),  # north
        (3, -1, 0): StringTag("right"),  # south
        (4, 0, -1): StringTag("right"),  # west
        (5, 0, 1): StringTag("right"),  # east
    },
)

bedrock_chest_connection_self = _bedrock_chest_connection(
    "facing_direction",
    {
        (2, -1, 0): StringTag("right"),  # north
        (2, 1, 0): StringTag("left"),  # north
        (3, 1, 0): StringTag("right"),  # south
        (3, -1, 0): StringTag("left"),  # south
        (4, 0, 1): StringTag("right"),  # west
        (4, 0, -1): StringTag("left"),  # west
        (5, 0, -1): StringTag("right"),  # east
        (5, 0, 1): StringTag("left"),  # east
    },
)

bedrock_chest_connection_other_left_120 = _bedrock_chest_connection(
    "minecraft:cardinal_direction",
    {
        ("north", -1, 0): StringTag("left"),  # north
        ("south", 1, 0): StringTag("left"),  # south
        ("west", 0, 1): StringTag("left"),  # west
        ("east", 0, -1): StringTag("left"),  # east
    },
)

bedrock_chest_connection_other_right_120 = _bedrock_chest_connection(
    "minecraft:cardinal_direction",
    {
        ("north", 1, 0): StringTag("right"),  # north
        ("south", -1, 0): StringTag("right"),  # south
        ("west", 0, -1): StringTag("right"),  # west
        ("east", 0, 1): StringTag("right"),  # east
    },
)

bedrock_chest_connection_self_120 = _bedrock_chest_connection(
    "minecraft:cardinal_direction",
    {
        ("north", -1, 0): StringTag("right"),  # north
        ("north", 1, 0): StringTag("left"),  # north
        ("south", 1, 0): StringTag("right"),  # south
        ("south", -1, 0): StringTag("left"),  # south
        ("west", 0, 1): StringTag("right"),  # west
        ("west", 0, -1): StringTag("left"),  # west
        ("east", 0, -1): StringTag("right"),  # east
        ("east", 0, 1): StringTag("left"),  # east
    },
)


def from_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    block = src.block
    if block is None:
        return

    extra = src.extra
    if extra is None:
        dst.extra_needed = True
        return

    facing = block.properties.get("facing")
    if not isinstance(facing, StringTag):
        return

    x, _, z = extra.absolute_coordinates
    facing_str = facing.py_str
    if facing_str == "north":
        dst.nbt.append(("", CompoundTag, (), "pairlead", ByteTag(1)))
        dst.nbt.append(("", CompoundTag, (), "pairx", IntTag(x - 1)))
        dst.nbt.append(("", CompoundTag, (), "pairz", IntTag(z)))
    elif facing_str == "south":
        dst.nbt.append(("", CompoundTag, (), "pairlead", ByteTag(1)))
        dst.nbt.append(("", CompoundTag, (), "pairx", IntTag(x + 1)))
        dst.nbt.append(("", CompoundTag, (), "pairz", IntTag(z)))
    elif facing_str == "west":
        dst.nbt.append(("", CompoundTag, (), "pairlead", ByteTag(1)))
        dst.nbt.append(("", CompoundTag, (), "pairx", IntTag(x)))
        dst.nbt.append(("", CompoundTag, (), "pairz", IntTag(z + 1)))
    elif facing_str == "east":
        dst.nbt.append(("", CompoundTag, (), "pairlead", ByteTag(1)))
        dst.nbt.append(("", CompoundTag, (), "pairx", IntTag(x)))
        dst.nbt.append(("", CompoundTag, (), "pairz", IntTag(z - 1)))

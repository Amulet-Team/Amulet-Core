from amulet_nbt import CompoundTag, ByteTag, IntTag, StringTag
from .._state import SrcData, StateData, DstData


def main(src: SrcData, state: StateData, dst: DstData) -> None:
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

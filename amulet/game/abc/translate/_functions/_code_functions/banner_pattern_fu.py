from amulet_nbt import CompoundTag, ListTag, IntTag
from .._state import SrcData, StateData, DstData


def main(src: SrcData, state: StateData, dst: DstData) -> None:
    nbt = src.nbt
    if nbt is None:
        return

    tag = nbt.tag
    if not isinstance(tag, CompoundTag):
        return

    utags = tag.get("utags")
    if not isinstance(utags, CompoundTag):
        return

    patterns = utags.get("Patterns")
    if not isinstance(patterns, ListTag):
        return

    for index, pattern in enumerate(patterns):
        if not isinstance(pattern, CompoundTag):
            continue
        colour = pattern.get("Color")
        if not isinstance(colour, IntTag):
            continue
        dst.nbt.append((
            "",
            CompoundTag,
            (("Patterns", ListTag), (index, CompoundTag)),
            "Color",
            IntTag(15 - colour.py_int)
        ))

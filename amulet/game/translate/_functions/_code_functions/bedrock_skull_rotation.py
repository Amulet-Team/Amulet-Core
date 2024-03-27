from amulet_nbt import CompoundTag, FloatTag, StringTag
from .._state import SrcData, StateData, DstData


def to_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    nbt = src.nbt
    if nbt is not None:
        tag = nbt.tag
        if isinstance(tag, CompoundTag):
            rotation = tag.get("Rotation")
            if isinstance(rotation, FloatTag):
                dst.properties["rotation"] = StringTag(
                    f"{int(rotation.py_float // 22.5) % 16}"
                )
                return
    dst.properties["rotation"] = StringTag("0")

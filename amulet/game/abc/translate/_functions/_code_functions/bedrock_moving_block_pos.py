from amulet_nbt import CompoundTag, IntTag
from .._state import SrcData, StateData, DstData


def to_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    if src.extra is None:
        return

    x, y, z = src.extra.absolute_coordinates

    nbt = src.nbt
    if nbt is None:
        return

    tag = nbt.tag
    if not isinstance(tag, CompoundTag):
        return

    pistonPosX = tag.get("pistonPosX")
    if not isinstance(pistonPosX, IntTag):
        return
    pistonPosY = tag.get("pistonPosY")
    if not isinstance(pistonPosY, IntTag):
        return
    pistonPosZ = tag.get("pistonPosZ")
    if not isinstance(pistonPosZ, IntTag):
        return

    dst.nbt.append(
        (
            "",
            CompoundTag,
            (("utags", CompoundTag),),
            "pistonPosdX",
            IntTag(pistonPosX.py_int - x),
        )
    )
    dst.nbt.append(
        (
            "",
            CompoundTag,
            (("utags", CompoundTag),),
            "pistonPosdY",
            IntTag(pistonPosY.py_int - y),
        )
    )
    dst.nbt.append(
        (
            "",
            CompoundTag,
            (("utags", CompoundTag),),
            "pistonPosdZ",
            IntTag(pistonPosZ.py_int - z),
        )
    )


def from_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    if src.extra is None:
        return

    x, y, z = src.extra.absolute_coordinates

    nbt = src.nbt
    if nbt is None:
        return

    tag = nbt.tag
    if not isinstance(tag, CompoundTag):
        return

    utags = tag.get("utags")
    if not isinstance(utags, CompoundTag):
        return

    pistonPosdX = utags.get("pistonPosdX")
    if not isinstance(pistonPosdX, IntTag):
        return
    pistonPosdY = utags.get("pistonPosdY")
    if not isinstance(pistonPosdY, IntTag):
        return
    pistonPosdZ = utags.get("pistonPosdZ")
    if not isinstance(pistonPosdZ, IntTag):
        return

    dst.nbt.append(("", CompoundTag, (), "pistonPosX", IntTag(pistonPosdX.py_int + x)))
    dst.nbt.append(("", CompoundTag, (), "pistonPosY", IntTag(pistonPosdY.py_int + y)))
    dst.nbt.append(("", CompoundTag, (), "pistonPosZ", IntTag(pistonPosdZ.py_int + z)))

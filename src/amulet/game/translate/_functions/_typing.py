from __future__ import annotations

from typing import Union, Type, TypeAlias
from collections.abc import Iterable

from amulet_nbt import (
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    FloatTag,
    DoubleTag,
    StringTag,
    ListTag,
    CompoundTag,
    ByteArrayTag,
    IntArrayTag,
    LongArrayTag,
)

NBTTagT: TypeAlias = Union[
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    FloatTag,
    DoubleTag,
    ByteArrayTag,
    StringTag,
    ListTag,
    CompoundTag,
    IntArrayTag,
    LongArrayTag,
]

NBTTagClasses = (
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    FloatTag,
    DoubleTag,
    ByteArrayTag,
    StringTag,
    ListTag,
    CompoundTag,
    IntArrayTag,
    LongArrayTag,
)

NBTTagClsT: TypeAlias = Union[
    Type[ByteTag],
    Type[ShortTag],
    Type[IntTag],
    Type[LongTag],
    Type[FloatTag],
    Type[DoubleTag],
    Type[ByteArrayTag],
    Type[StringTag],
    Type[ListTag],
    Type[CompoundTag],
    Type[IntArrayTag],
    Type[LongArrayTag],
]

StrToNBTCls = {
    "byte": ByteTag,
    "short": ShortTag,
    "int": IntTag,
    "long": LongTag,
    "float": FloatTag,
    "double": DoubleTag,
    "byte_array": ByteArrayTag,
    "string": StringTag,
    "list": ListTag,
    "compound": CompoundTag,
    "int_array": IntArrayTag,
    "long_array": LongArrayTag,
}

NBTClsToStr = {
    ByteTag: "byte",
    ShortTag: "short",
    IntTag: "int",
    LongTag: "long",
    FloatTag: "float",
    DoubleTag: "double",
    ByteArrayTag: "byte_array",
    StringTag: "string",
    ListTag: "list",
    CompoundTag: "compound",
    IntArrayTag: "int_array",
    LongArrayTag: "long_array",
}


NBTPathElement: TypeAlias = tuple[str | int, NBTTagClsT]
NBTPath: TypeAlias = tuple[NBTPathElement, ...]

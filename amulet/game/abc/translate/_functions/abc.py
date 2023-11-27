from __future__ import annotations

from typing import (
    Union,
    Type,
    Sequence,
    Optional,
    Callable,
    Self,
    Any,
)
from collections.abc import Mapping
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

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
    NamedTag,
    from_snbt,
)

from amulet.block import Block, PropertyValueType, PropertyValueClasses
from amulet.api.data_types import BlockCoordinates
from ..._json_interface import JSONInterface, JSONCompatible, JSONDict, JSONList

NBTTagT = Union[
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

NBTTagClsT = Union[
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


@dataclass
class SrcData:
    """Input data. This must not be changed."""

    block_input: Optional[Block]
    nbt_input: Optional[NamedTag]
    get_block_callback: Optional[Callable]
    absolute_location: BlockCoordinates = (0, 0, 0)


@dataclass
class StateData:
    relative_location: BlockCoordinates = (0, 0, 0)
    nbt_path: tuple[str, str, list[tuple[Union[str, int], str]]] = None
    inherited_data: tuple[Union[str, None], Union[str, None], dict, bool, bool] = None


@dataclass
class DstData:
    output_type: Optional[str] = None
    output_name: Optional[str] = None
    properties: dict[str, PropertyValueType] = field(default_factory=dict)
    nbt: list[
        tuple[
            str,
            str,
            list[Union[str, int], str],
            Union[str, int],
            NBTTagT,
        ]
    ] = field(default_factory=list)
    extra_needed: bool = False
    cacheable: bool = True


def immutable_from_snbt(snbt: str) -> PropertyValueType:
    val = from_snbt(snbt)
    if not isinstance(val, PropertyValueClasses):
        raise TypeError
    return val


def from_json(data: JSONCompatible) -> AbstractBaseTranslationFunction:
    if isinstance(data, Sequence):
        func_cls = _translation_functions["sequence"]
        return func_cls.from_json(data)
    elif isinstance(data, Mapping):
        func_cls = _translation_functions[data["function"]]
        return func_cls.from_json(data)
    else:
        raise TypeError


_translation_functions: dict[str, type[AbstractBaseTranslationFunction]] = {}


class AbstractBaseTranslationFunction(JSONInterface, ABC):
    Name: str = None

    def __init_subclass__(cls, **kwargs) -> None:
        if cls.Name is None:
            raise RuntimeError(f"Name attribute has not been set for {cls}")
        if cls.Name in _translation_functions:
            raise RuntimeError(
                f"A translation function with name {cls.Name} already exists."
            )
        _translation_functions[cls.Name] = cls

    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def run(self, *args, **kwargs):
        """Run the translation function"""
        raise NotImplementedError

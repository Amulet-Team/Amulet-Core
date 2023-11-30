from __future__ import annotations

from typing import Union, Type, Optional, Callable, Any, Protocol
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
from amulet.block_entity import BlockEntity
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

    src_block: Optional[Block]
    src_nbt: Optional[NamedTag]
    extra: tuple[
        BlockCoordinates,
        Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
    ]


@dataclass
class StateData:
    relative_location: BlockCoordinates = (0, 0, 0)
    nbt_path: tuple[str, str, list[tuple[Union[str, int], str]]] | None = None
    inherited_data: tuple[
        Union[str, None], Union[str, None], dict, bool, bool
    ] | None = None


@dataclass
class DstData:
    output_type: Optional[str] = None
    output_name: Optional[str] = None
    properties: dict[str, PropertyValueType] = field(default_factory=dict)
    nbt: list[
        tuple[
            str,
            str,
            tuple[tuple[str | int, str]],
            Union[str, int],
            NBTTagT,
        ]
    ] = field(default_factory=list)
    extra_needed: bool = False
    cacheable: bool = True


def immutable_from_snbt(snbt: str) -> PropertyValueType:
    val = from_snbt(snbt)
    assert isinstance(val, PropertyValueClasses)
    return val


def from_json(data: JSONCompatible) -> AbstractBaseTranslationFunction:
    if isinstance(data, list):
        func_cls = _translation_functions["sequence"]
        return func_cls.from_json(data)
    elif isinstance(data, dict):
        function_name = data["function"]
        assert isinstance(function_name, str)
        func_cls = _translation_functions[function_name]
        return func_cls.from_json(data)
    else:
        raise TypeError


_translation_functions: dict[str, type[AbstractBaseTranslationFunction]] = {}


class Data(Protocol):
    def __hash__(self) -> int:
        ...

    def __eq__(self, other: Any) -> bool:
        ...


class AbstractBaseTranslationFunction(JSONInterface, ABC):
    Name: str = ""

    def __init_subclass__(cls, **kwargs) -> None:
        if cls.Name == "":
            raise RuntimeError(f"Name attribute has not been set for {cls}")
        if cls.Name in _translation_functions:
            raise RuntimeError(
                f"A translation function with name {cls.Name} already exists."
            )
        _translation_functions[cls.Name] = cls

    @abstractmethod
    def _data(self) -> Data:
        raise NotImplementedError

    def __bool__(self) -> bool:
        return True

    def __hash__(self) -> int:
        return hash(self._data())

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._data() == other._data()

    @abstractmethod
    def run(self, *args, **kwargs):
        """Run the translation function"""
        raise NotImplementedError

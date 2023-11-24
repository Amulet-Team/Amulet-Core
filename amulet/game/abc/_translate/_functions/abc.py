from __future__ import annotations

from typing import (
    Union,
    Type,
    Sequence,
    Optional,
    Callable,
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
)

from amulet.block import Block, PropertyValueType
from amulet.api.data_types import BlockCoordinates

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


def from_json(data) -> AbstractBaseTranslationFunction:
    if isinstance(data, Sequence):
        func_cls = _translation_functions["sequence"]
        return func_cls.from_json(data)
    elif isinstance(data, Mapping):
        func_cls = _translation_functions[data["function"]]
        return func_cls.from_json(data)
    else:
        raise TypeError


_translation_functions: dict[str, type[AbstractBaseTranslationFunction]] = {}


class AbstractBaseTranslationFunction(ABC):
    Name: str = None
    _instances = {}

    @abstractmethod
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        if cls.Name is None:
            raise RuntimeError(f"Name attribute has not been set for {cls}")
        if cls.Name in _translation_functions:
            raise RuntimeError(
                f"A translation function with name {cls.Name} already exists."
            )
        _translation_functions[cls.Name] = cls

    @classmethod
    @abstractmethod
    def instance(cls, *args, **kwargs) -> AbstractBaseTranslationFunction:
        """
        Get the translation function for this data.
        This will return a cached instance if it already exists.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_json(cls, data) -> AbstractBaseTranslationFunction:
        """Get a translation function from the JSON representation."""
        raise NotImplementedError

    @abstractmethod
    def to_json(self):
        """Convert the translation function back to the JSON representation."""
        raise NotImplementedError

    @abstractmethod
    def run(self, *args, **kwargs):
        """Run the translation function"""
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

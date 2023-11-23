from __future__ import annotations

from typing import (
    Union,
    Type,
    Sequence,
    Optional,
    Callable,
    TypeVar,
    Iterator,
)
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from inspect import isclass

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
    from_snbt,
    NamedTag,
    AbstractBaseTag,
)

from PyMCTranslate.py3.api import Block, BlockEntity, Entity, ChunkLoadError

K = TypeVar("K")
V = TypeVar("V")


BlockCoordinates = tuple[int, int, int]
PropertyValueClasses = (ByteTag, IntTag, StringTag)
PropertyValueType = Union[ByteTag, IntTag, StringTag]

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


class HashableMapping(Mapping[K, V]):
    """
    A hashable Mapping class.
    All values in the mapping must be hashable.
    """

    def __init__(self, mapping: Mapping):
        self._map = dict(mapping)
        self._hash = hash(frozenset(mapping.items()))

    def __getitem__(self, k: K) -> V:
        return self._map[k]

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[K]:
        return iter(self._map)

    def __hash__(self):
        return self._hash


_translation_functions: dict[str, Type[AbstractBaseTranslationFunction]] = {}


def from_json(data) -> AbstractBaseTranslationFunction:
    if isinstance(data, (list, Sequence)):
        return TranslationFunctionSequence.from_json(data)
    elif isinstance(data, (dict, Mapping)):
        func_cls = _translation_functions[data["function"]]
        return func_cls.from_json(data)
    else:
        raise TypeError


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


class TranslationFunctionSequence(AbstractBaseTranslationFunction):
    # class variables
    Name = "sequence"

    # instance variables
    _functions: tuple[AbstractBaseTranslationFunction]

    def __init__(self, functions: Sequence[AbstractBaseTranslationFunction]):
        self._functions = tuple(functions)
        if not all(
            isinstance(inst, AbstractBaseTranslationFunction)
            for inst in self._functions
        ):
            raise TypeError

    @classmethod
    def instance(
        cls, functions: Sequence[AbstractBaseTranslationFunction]
    ) -> TranslationFunctionSequence:
        self = cls(functions)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: list) -> TranslationFunctionSequence:
        parsed = []
        for func in data:
            parsed.append(from_json(func))

        return cls.instance(parsed)

    def to_json(self) -> list:
        return [func.to_json() for func in self._functions]

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._functions)

    def __eq__(self, other):
        if not isinstance(other, TranslationFunctionSequence):
            return NotImplemented
        return self._functions == other._functions


class NewBlock(AbstractBaseTranslationFunction):
    # class variables
    Name = "new_block"

    # instance variables
    _block: str

    def __init__(self, block: str):
        if not isinstance(block, str):
            raise TypeError
        self._block = block

    @classmethod
    def instance(cls, block: str) -> NewBlock:
        self = cls(block)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> NewBlock:
        if data.get("function") != "new_block":
            raise ValueError("Incorrect function data given.")
        return cls.instance(data["options"])

    def to_json(self) -> dict:
        return {"function": "new_block", "options": self._block}

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._block)

    def __eq__(self, other):
        if not isinstance(other, NewBlock):
            return NotImplemented
        return self._block == other._block


class NewEntity(AbstractBaseTranslationFunction):
    # class variables
    Name = "new_entity"

    # instance variables
    _entity: str

    def __init__(self, entity: str):
        if not isinstance(entity, str):
            raise TypeError
        self._entity = entity

    @classmethod
    def instance(cls, entity: str) -> NewEntity:
        self = cls(entity)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> NewEntity:
        if data.get("function") != "new_entity":
            raise ValueError("Incorrect function data given.")
        return cls.instance(data["options"])

    def to_json(self) -> dict:
        return {"function": "new_entity", "options": self._entity}

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._entity)

    def __eq__(self, other):
        if not isinstance(other, NewEntity):
            return NotImplemented
        return self._entity == other._entity


class NewProperties(AbstractBaseTranslationFunction):
    # class variables
    Name = "new_properties"
    _instances = {}

    # instance variables
    _properties: HashableMapping[str, PropertyValueType]

    def __init__(self, properties: Mapping[str, PropertyValueType]):
        self._properties = HashableMapping(properties)
        if not all(isinstance(key, str) for key in self._properties.keys()):
            raise TypeError
        if not all(
            isinstance(value, PropertyValueClasses)
            for value in self._properties.values()
        ):
            raise TypeError

    @classmethod
    def instance(cls, properties: Mapping[str, PropertyValueType]) -> NewProperties:
        self = cls(properties)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: dict) -> NewProperties:
        if data.get("function") != "new_properties":
            raise ValueError("Incorrect function data given.")
        return cls.instance(
            {
                property_name: from_snbt(snbt)
                for property_name, snbt in data["options"].items()
            }
        )

    def to_json(self) -> dict:
        return {
            "function": "new_properties",
            "options": {
                property_name: tag.to_snbt()
                for property_name, tag in self._properties.items()
            },
        }

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __hash__(self):
        return hash(self._properties)

    def __eq__(self, other):
        if not isinstance(other, NewProperties):
            return NotImplemented
        return self._properties == other._properties


class MapProperties(AbstractBaseTranslationFunction):
    # class variables
    Name = "map_properties"
    _instances = {}

    # instance variables
    _properties: HashableMapping[
        str, HashableMapping[PropertyValueType, AbstractBaseTranslationFunction]
    ]

    def __init__(
        self,
        properties: Mapping[
            str, Mapping[PropertyValueType, AbstractBaseTranslationFunction]
        ],
    ):
        hashable_properties = {}

        for prop, data in properties.items():
            if not isinstance(prop, str):
                raise TypeError
            hashable_data = HashableMapping(data)
            for val, func in hashable_data.items():
                if not isinstance(val, PropertyValueClasses):
                    raise TypeError
                if not isinstance(func, AbstractBaseTranslationFunction):
                    raise TypeError
            hashable_properties[prop] = hashable_data

        self._properties = HashableMapping(hashable_properties)

    @classmethod
    def instance(
        cls,
        properties: Mapping[
            str, Mapping[PropertyValueType, AbstractBaseTranslationFunction]
        ],
    ) -> MapProperties:
        self = cls(properties)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> MapProperties:
        if data.get("function") != "map_properties":
            raise ValueError("Incorrect function data given.")
        return cls.instance(
            {
                property_name: {
                    from_snbt(snbt): from_json(func) for snbt, func in mapping.items
                }
                for property_name, mapping in data["options"].items()
            }
        )

    def to_json(self):
        return {
            "function": "map_properties",
            "options": {
                property_name: {
                    nbt.to_snbt(): func.to_json() for nbt, func in mapping.items()
                }
                for property_name, mapping in self._properties.items()
            },
        }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._properties)

    def __eq__(self, other):
        if not isinstance(other, MapProperties):
            return NotImplemented
        return self._properties == other._properties


class MultiBlock(AbstractBaseTranslationFunction):
    Name = "multiblock"
    _blocks: tuple[tuple[BlockCoordinates, AbstractBaseTranslationFunction], ...]

    def __init__(
        self, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]
    ):
        self._blocks = tuple(blocks)
        for coords, func in self._blocks:
            if (
                not isinstance(coords, tuple)
                and len(coords) == 3
                and all(isinstance(v, int) for v in coords)
            ):
                raise TypeError
            if not isinstance(func, AbstractBaseTranslationFunction):
                raise TypeError

    @classmethod
    def instance(
        cls, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]
    ) -> MultiBlock:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> MultiBlock:
        if data.get("function") != "multiblock":
            raise ValueError("Incorrect function data given.")
        return cls.instance(
            [(block["coords"], block["functions"]) for block in data["options"]]
        )

    def to_json(self):
        return {
            "function": "multiblock",
            "options": [
                {"coords": list(coords), "functions": func.to_json()}
                for coords, func in self._blocks
            ],
        }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, MultiBlock):
            return NotImplemented
        return self._blocks == other._blocks


class MapBlockName(AbstractBaseTranslationFunction):
    Name = "map_block_name"
    _blocks: HashableMapping[str, AbstractBaseTranslationFunction]

    def __init__(
            self, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ):
        self._blocks = HashableMapping(blocks)
        for block_name, func in self._blocks.items():
            if not isinstance(block_name, str):
                raise TypeError
            if not isinstance(func, AbstractBaseTranslationFunction):
                raise TypeError

    @classmethod
    def instance(
            cls, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ) -> MapBlockName:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> MapBlockName:
        if data.get("function") != "map_block_name":
            raise ValueError("Incorrect function data given.")
        return cls.instance({
            block_name: from_json(function) for block_name, function in data["options"].items()
        })

    def to_json(self):
        return {
            "function": "map_block_name",
            "options": {
                block_name: func.to_json() for block_name, func in self._blocks.items()
            },
        }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, MapBlockName):
            return NotImplemented
        return self._blocks == other._blocks


class WalkInputNBT(AbstractBaseTranslationFunction):
    Name = "walk_input_nbt"
    _blocks: HashableMapping[str, AbstractBaseTranslationFunction]

    def __init__(
            self, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ):
        # self._blocks = HashableMapping(blocks)
        # for block_name, func in self._blocks.items():
        #     if not isinstance(block_name, str):
        #         raise TypeError
        #     if not isinstance(func, AbstractBaseTranslationFunction):
        #         raise TypeError

    @classmethod
    def instance(
            cls, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ) -> WalkInputNBT:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> WalkInputNBT:
        # if data.get("function") != "map_block_name":
        #     raise ValueError("Incorrect function data given.")
        # return cls.instance({
        #     block_name: from_json(function) for block_name, function in data["options"].items()
        # })

    def to_json(self):
        # return {
        #     "function": "map_block_name",
        #     "options": {
        #         block_name: func.to_json() for block_name, func in self._blocks.items()
        #     },
        # }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, WalkInputNBT):
            return NotImplemented
        return self._blocks == other._blocks


class NewNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_nbt"

    # Instance variables
    _outer_name: str
    _outer_type: NBTTagClsT
    _path: Optional[tuple[tuple[Union[str, int], str], ...]]
    _key: Union[str, int]
    _value: NBTTagT

    def __init__(
        self,
        outer_name: str,
        outer_type: NBTTagClsT,
        path: Optional[Sequence[tuple[Union[str, int], NBTTagClsT]]],
        key: Union[str, int],
        value: NBTTagT
    ):
        if not isinstance(outer_name, str):
            raise TypeError
        self._outer_name = outer_name

        if outer_type not in NBTClsToStr:
            raise ValueError
        self._outer_type = outer_type

        if path is not None:
            path = list(path)
            for i, (key, val) in enumerate(path):
                if val not in {CompoundTag, ListTag}: #, ByteArrayTag, IntArrayTag, LongArrayTag}:
                    raise ValueError

                if i:
                    last_cls = path[i-1][1]
                else:
                    last_cls = self._outer_type

                if isinstance(key, str):
                    if last_cls is not CompoundTag:
                        raise TypeError
                elif isinstance(key, int):
                    if last_cls not in {ListTag, ByteArrayTag, IntArrayTag, LongArrayTag}:
                        raise TypeError
                else:
                    raise TypeError

                path[i] = (key, val)
            path = tuple(path)
        self._path = path

        # TODO: validate this better
        if not isinstance(key, (str, int)):
            raise TypeError
        self._key = key

        if not isinstance(value, NBTTagClasses):
            raise TypeError
        self._value = value

    @classmethod
    def instance(
            cls, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ) -> NewNBT:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> NewNBT:
        if data.get("function") != "new_nbt":
            raise ValueError("Incorrect function data given.")
        return cls.instance({
            block_name: from_json(function) for block_name, function in data["options"].items()
        })

    def to_json(self):

    # return {
    #     "function": "map_block_name",
    #     "options": {
    #         block_name: func.to_json() for block_name, func in self._blocks.items()
    #     },
    # }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, NewNBT):
            return NotImplemented
        return self._blocks == other._blocks


class CarryNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "carry_nbt"

    # Instance variables
    _blocks: HashableMapping[str, AbstractBaseTranslationFunction]

    def __init__(
            self, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ):

    # self._blocks = HashableMapping(blocks)
    # for block_name, func in self._blocks.items():
    #     if not isinstance(block_name, str):
    #         raise TypeError
    #     if not isinstance(func, AbstractBaseTranslationFunction):
    #         raise TypeError

    @classmethod
    def instance(
            cls, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ) -> CarryNBT:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> CarryNBT:

    # if data.get("function") != "map_block_name":
    #     raise ValueError("Incorrect function data given.")
    # return cls.instance({
    #     block_name: from_json(function) for block_name, function in data["options"].items()
    # })

    def to_json(self):

    # return {
    #     "function": "map_block_name",
    #     "options": {
    #         block_name: func.to_json() for block_name, func in self._blocks.items()
    #     },
    # }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, CarryNBT):
            return NotImplemented
        return self._blocks == other._blocks


class MapNBT(AbstractBaseTranslationFunction):
    # Class variables
    Name = "map_nbt"

    # Instance variables
    _blocks: HashableMapping[str, AbstractBaseTranslationFunction]

    def __init__(
            self, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ):

    # self._blocks = HashableMapping(blocks)
    # for block_name, func in self._blocks.items():
    #     if not isinstance(block_name, str):
    #         raise TypeError
    #     if not isinstance(func, AbstractBaseTranslationFunction):
    #         raise TypeError

    @classmethod
    def instance(
            cls, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ) -> MapNBT:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> MapNBT:

    # if data.get("function") != "map_block_name":
    #     raise ValueError("Incorrect function data given.")
    # return cls.instance({
    #     block_name: from_json(function) for block_name, function in data["options"].items()
    # })

    def to_json(self):

    # return {
    #     "function": "map_block_name",
    #     "options": {
    #         block_name: func.to_json() for block_name, func in self._blocks.items()
    #     },
    # }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, MapNBT):
            return NotImplemented
        return self._blocks == other._blocks


class Code(AbstractBaseTranslationFunction):
    # Class variables
    Name = "code"

    # Instance variables
    _blocks: HashableMapping[str, AbstractBaseTranslationFunction]

    def __init__(
            self, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ):

    # self._blocks = HashableMapping(blocks)
    # for block_name, func in self._blocks.items():
    #     if not isinstance(block_name, str):
    #         raise TypeError
    #     if not isinstance(func, AbstractBaseTranslationFunction):
    #         raise TypeError

    @classmethod
    def instance(
            cls, blocks: Mapping[str, AbstractBaseTranslationFunction]
    ) -> Code:
        self = cls(blocks)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data) -> Code:

    # if data.get("function") != "map_block_name":
    #     raise ValueError("Incorrect function data given.")
    # return cls.instance({
    #     block_name: from_json(function) for block_name, function in data["options"].items()
    # })

    def to_json(self):

    # return {
    #     "function": "map_block_name",
    #     "options": {
    #         block_name: func.to_json() for block_name, func in self._blocks.items()
    #     },
    # }

    def run(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash(self._blocks)

    def __eq__(self, other):
        if not isinstance(other, Code):
            return NotImplemented
        return self._blocks == other._blocks

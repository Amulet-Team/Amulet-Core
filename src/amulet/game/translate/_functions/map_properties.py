from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping

from amulet.block import PropertyValueType, Block
from .abc import (
    AbstractBaseTranslationFunction,
    immutable_from_snbt,
    translation_function_from_json,
    Data,
)
from amulet.game.abc import JSONCompatible, JSONDict
from ._frozen import FrozenMapping
from ._state import SrcData, StateData, DstData


class MapProperties(AbstractBaseTranslationFunction):
    # Class variables
    Name = "map_properties"
    _instances = {}

    # Instance variables
    _properties: FrozenMapping[
        str, FrozenMapping[PropertyValueType, AbstractBaseTranslationFunction]
    ]

    def __init__(
        self,
        properties: Mapping[
            str, Mapping[PropertyValueType, AbstractBaseTranslationFunction]
        ],
    ) -> None:
        super().__init__()
        hashable_properties = {}

        for prop, data in properties.items():
            assert isinstance(prop, str)
            hashable_data = FrozenMapping[
                PropertyValueType, AbstractBaseTranslationFunction
            ](data)
            for val, func in hashable_data.items():
                assert isinstance(val, PropertyValueType)
                assert isinstance(func, AbstractBaseTranslationFunction)
            hashable_properties[prop] = hashable_data

        self._properties = FrozenMapping[
            str, FrozenMapping[PropertyValueType, AbstractBaseTranslationFunction]
        ](hashable_properties)

    def __reduce__(self) -> Any:
        return MapProperties, (self._properties,)

    def _data(self) -> Data:
        return self._properties

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "map_properties"
        options = data["options"]
        assert isinstance(options, dict)
        properties = {}
        for property_name, mapping in options.items():
            assert isinstance(property_name, str)
            assert isinstance(mapping, dict)
            values = {}
            for snbt, func in mapping.items():
                assert isinstance(snbt, str)
                assert isinstance(func, dict | list)
                values[immutable_from_snbt(snbt)] = translation_function_from_json(func)
            properties[property_name] = values
        return cls(properties)

    def to_json(self) -> JSONDict:
        return {
            "function": "map_properties",
            "options": {
                property_name: {
                    nbt.to_snbt(): func.to_json() for nbt, func in mapping.items()
                }
                for property_name, mapping in self._properties.items()
            },
        }

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        block = src.block
        assert isinstance(block, Block)
        src_properties = block.properties
        for key, options in self._properties.items():
            val = src_properties.get(key)
            if val is not None and val in options:
                options[val].run(src, state, dst)

from __future__ import annotations

from typing import Self
from collections.abc import Mapping

from amulet.block import PropertyValueType, PropertyValueClasses
from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    immutable_from_snbt,
    from_json,
    Data,
)
from ._frozen import FrozenMapping


class MapProperties(AbstractBaseTranslationFunction):
    # Class variables
    Name = "map_properties"
    _instances: dict[MapProperties, MapProperties] = {}

    # Instance variables
    _properties: FrozenMapping[
        str, FrozenMapping[PropertyValueType, AbstractBaseTranslationFunction]
    ]

    def __new__(
        cls,
        properties: Mapping[
            str, Mapping[PropertyValueType, AbstractBaseTranslationFunction]
        ],
    ) -> MapProperties:
        self = super().__new__(cls)

        hashable_properties = {}

        for prop, data in properties.items():
            assert isinstance(prop, str)
            hashable_data = FrozenMapping[
                PropertyValueType, AbstractBaseTranslationFunction
            ](data)
            for val, func in hashable_data.items():
                assert isinstance(val, PropertyValueClasses)
                assert isinstance(func, AbstractBaseTranslationFunction)
            hashable_properties[prop] = hashable_data

        self._properties = FrozenMapping[
            str, FrozenMapping[PropertyValueType, AbstractBaseTranslationFunction]
        ](hashable_properties)
        return cls._instances.setdefault(self, self)

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
                values[immutable_from_snbt(snbt)] = from_json(func)
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

    def run(self, *args, **kwargs):
        pass

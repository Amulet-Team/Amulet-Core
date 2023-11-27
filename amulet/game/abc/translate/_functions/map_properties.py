from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping

from amulet.block import PropertyValueType, PropertyValueClasses
from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    immutable_from_snbt,
    from_json,
)
from ._frozen import FrozenMapping


class MapProperties(AbstractBaseTranslationFunction):
    # Class variables
    Name = "map_properties"
    _instances: dict[Self, Self] = {}

    def __new__(
        cls,
        properties: Mapping[
            str, Mapping[PropertyValueType, AbstractBaseTranslationFunction]
        ],
    ) -> Self:
        self = super().__new__(cls)

        hashable_properties = {}

        for prop, data in properties.items():
            if not isinstance(prop, str):
                raise TypeError
            hashable_data = FrozenMapping(data)
            for val, func in hashable_data.items():
                if not isinstance(val, PropertyValueClasses):
                    raise TypeError
                if not isinstance(func, AbstractBaseTranslationFunction):
                    raise TypeError
            hashable_properties[prop] = hashable_data

        self._properties = FrozenMapping[
            str, FrozenMapping[PropertyValueType, AbstractBaseTranslationFunction]
        ](hashable_properties)
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        if data.get("function") != "map_properties":
            raise ValueError("Incorrect function data given.")
        return cls(
            {
                property_name: {
                    immutable_from_snbt(snbt): from_json(func)
                    for snbt, func in mapping.items()
                }
                for property_name, mapping in data["options"].items()
            }
        )

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

    def __hash__(self) -> int:
        return hash(self._properties)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MapProperties):
            return NotImplemented
        return self._properties == other._properties

    def run(self, *args, **kwargs):
        pass

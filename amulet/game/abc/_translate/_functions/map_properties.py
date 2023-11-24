from __future__ import annotations

from collections.abc import Mapping

from amulet_nbt import from_snbt

from amulet.block import PropertyValueType, PropertyValueClasses
from .abc import AbstractBaseTranslationFunction
from ._frozen_map import FrozenMapping


class MapProperties(AbstractBaseTranslationFunction):
    # class variables
    Name = "map_properties"
    _instances = {}

    # instance variables
    _properties: FrozenMapping[
        str, FrozenMapping[PropertyValueType, AbstractBaseTranslationFunction]
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
            hashable_data = FrozenMapping(data)
            for val, func in hashable_data.items():
                if not isinstance(val, PropertyValueClasses):
                    raise TypeError
                if not isinstance(func, AbstractBaseTranslationFunction):
                    raise TypeError
            hashable_properties[prop] = hashable_data

        self._properties = FrozenMapping(hashable_properties)

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

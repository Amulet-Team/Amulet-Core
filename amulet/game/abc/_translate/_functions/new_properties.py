from __future__ import annotations

from collections.abc import Mapping

from amulet_nbt import from_snbt

from amulet.block import Block, PropertyValueType, PropertyValueClasses
from .abc import AbstractBaseTranslationFunction
from ._frozen_map import FrozenMapping


class NewProperties(AbstractBaseTranslationFunction):
    # class variables
    Name = "new_properties"
    _instances = {}

    # instance variables
    _properties: FrozenMapping[str, PropertyValueType]

    def __init__(self, properties: Mapping[str, PropertyValueType]):
        self._properties = FrozenMapping(properties)
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

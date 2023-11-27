from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping

from amulet.block import Block, PropertyValueType, PropertyValueClasses
from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    immutable_from_snbt,
)
from ._frozen import FrozenMapping


class NewProperties(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_properties"
    _instances: dict[Self, Self] = {}

    def __new__(cls, properties: Mapping[str, PropertyValueType]) -> Self:
        self = super().__new__(cls)
        self._properties = FrozenMapping[str, PropertyValueType](properties)
        if not all(isinstance(key, str) for key in self._properties.keys()):
            raise TypeError
        if not all(
            isinstance(value, PropertyValueClasses)
            for value in self._properties.values()
        ):
            raise TypeError
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        if not isinstance(data, dict):
            raise TypeError
        if data.get("function") != "new_properties":
            raise ValueError("Incorrect function data given.")
        return cls(
            {
                property_name: immutable_from_snbt(snbt)
                for property_name, snbt in data["options"].items()
            }
        )

    def to_json(self) -> JSONDict:
        return {
            "function": "new_properties",
            "options": {
                property_name: tag.to_snbt()
                for property_name, tag in self._properties.items()
            },
        }

    def __hash__(self) -> int:
        return hash(self._properties)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NewProperties):
            return NotImplemented
        return self._properties == other._properties

    def run(self, *args, **kwargs):
        raise NotImplementedError

from __future__ import annotations

from typing import Self
from collections.abc import Mapping

from amulet.block import PropertyValueType, PropertyValueClasses
from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    immutable_from_snbt,
    Data,
)
from ._frozen import FrozenMapping
from ._state import SrcData, StateData, DstData


class NewProperties(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_properties"
    _instances: dict[NewProperties, NewProperties] = {}

    # Instance variables
    _properties: FrozenMapping[str, PropertyValueType]

    def __new__(cls, properties: Mapping[str, PropertyValueType]) -> NewProperties:
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

    def _data(self) -> Data:
        return self._properties

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "new_properties"
        options = data["options"]
        assert isinstance(options, dict)
        properties = {}
        for property_name, snbt in options.items():
            assert isinstance(property_name, str)
            assert isinstance(snbt, str)
            properties[property_name] = immutable_from_snbt(snbt)
        return cls(properties)

    def to_json(self) -> JSONDict:
        return {
            "function": "new_properties",
            "options": {
                property_name: tag.to_snbt()
                for property_name, tag in self._properties.items()
            },
        }

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        dst.properties.update(self._properties)

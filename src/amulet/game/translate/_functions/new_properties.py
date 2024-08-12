from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping

from amulet.block import PropertyValueType
from .abc import (
    AbstractBaseTranslationFunction,
    immutable_from_snbt,
    Data,
)
from amulet.game.abc import JSONCompatible, JSONDict
from ._frozen import FrozenMapping
from ._state import SrcData, StateData, DstData


class NewProperties(AbstractBaseTranslationFunction):
    # Class variables
    Name = "new_properties"
    _instances = {}

    # Instance variables
    _properties: FrozenMapping[str, PropertyValueType]

    def __init__(self, properties: Mapping[str, PropertyValueType]) -> None:
        super().__init__()
        self._properties = FrozenMapping[str, PropertyValueType](properties)
        if not all(isinstance(key, str) for key in self._properties.keys()):
            raise TypeError
        if not all(
            isinstance(value, PropertyValueType) for value in self._properties.values()
        ):
            raise TypeError

    def __reduce__(self) -> Any:
        return NewProperties, (self._properties,)

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

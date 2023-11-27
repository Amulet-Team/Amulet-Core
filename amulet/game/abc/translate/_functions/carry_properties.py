from __future__ import annotations

from typing import Self, Any
from collections.abc import Mapping, Iterable

from amulet.block import PropertyValueType, PropertyValueClasses

from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    immutable_from_snbt,
)
from ._frozen import FrozenMapping, OrderedFrozenSet


class CarryProperties(AbstractBaseTranslationFunction):
    # Class variables
    Name = "carry_properties"
    _instances: dict[Self, Self] = {}

    def __new__(cls, properties: Mapping[str, Iterable[PropertyValueType]]) -> Self:
        if not isinstance(properties, Mapping):
            raise TypeError
        frozen_properties = {}
        for key, val in properties.items():
            frozen_val = OrderedFrozenSet(val)
            if not (
                isinstance(key, str)
                and all(isinstance(v, PropertyValueClasses) for v in frozen_val)
            ):
                raise TypeError
            frozen_properties[key] = frozen_val
        self = super().__new__(cls)
        self._properties = FrozenMapping[str, OrderedFrozenSet[PropertyValueType]](
            frozen_properties
        )
        return cls._instances.setdefault(self, self)

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        if not isinstance(data, dict):
            raise TypeError
        if data.get("function") != "carry_properties":
            raise ValueError("Incorrect function data given.")
        return cls(
            {
                property_name: [immutable_from_snbt(snbt) for snbt in snbt_list]
                for property_name, snbt_list in data["options"].items()
            }
        )

    def to_json(self) -> JSONDict:
        return {
            "function": "carry_properties",
            "options": {
                key: [v.to_snbt() for v in val] for key, val in self._properties.items()
            },
        }

    def __hash__(self) -> int:
        return hash(self._properties)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CarryProperties):
            return NotImplemented
        return self._properties == other._properties

    def run(self, *args, **kwargs):
        raise NotImplementedError

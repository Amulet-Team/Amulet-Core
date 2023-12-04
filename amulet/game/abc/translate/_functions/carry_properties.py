from __future__ import annotations

from typing import Self
from collections.abc import Mapping, Iterable

from amulet.block import PropertyValueType, PropertyValueClasses, Block

from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    immutable_from_snbt,
    Data,
)
from ._frozen import FrozenMapping, OrderedFrozenSet
from ._state import SrcData, StateData, DstData


class CarryProperties(AbstractBaseTranslationFunction):
    # Class variables
    Name = "carry_properties"
    _instances: dict[CarryProperties, CarryProperties] = {}

    # Instance variables
    _properties: FrozenMapping[str, OrderedFrozenSet[PropertyValueType]]

    def __new__(
        cls, properties: Mapping[str, Iterable[PropertyValueType]]
    ) -> CarryProperties:
        assert isinstance(properties, Mapping)
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

    def _data(self) -> Data:
        return self._properties

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "carry_properties"
        options = data["options"]
        assert isinstance(options, dict)
        properties = {}
        for property_name, snbt_list in options.items():
            assert isinstance(property_name, str)
            assert isinstance(snbt_list, list)
            values = []
            for snbt in snbt_list:
                assert isinstance(snbt, str)
                values.append(immutable_from_snbt(snbt))
            properties[property_name] = values
        return cls(properties)

    def to_json(self) -> JSONDict:
        return {
            "function": "carry_properties",
            "options": {
                key: [v.to_snbt() for v in val] for key, val in self._properties.items()
            },
        }

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        block = src.block
        assert isinstance(block, Block)
        src_properties = block.properties
        for key, options in self._properties.items():
            val = src_properties.get(key)
            if val is not None and val in options:
                dst.properties[key] = val

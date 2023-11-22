from typing import Self
from types import MappingProxyType
from collections.abc import Mapping, Iterator
from dataclasses import dataclass

from amulet_nbt import from_snbt
from amulet.block import PropertyValueType, PropertyDataTypes

from ._json_interface import JSONInterface, JSONCompatible


def immutable_from_snbt(snbt: str) -> PropertyValueType:
    val = from_snbt(snbt)
    if not isinstance(val, PropertyDataTypes):
        raise TypeError
    return val


@dataclass(frozen=True)
class PropertyValueSpec:
    default: PropertyValueType
    states: tuple[PropertyValueType, ...]


class PropertySpec(Mapping[str, PropertyValueSpec]):
    def __init__(self, properties: Mapping[str, PropertyValueSpec] = MappingProxyType({})):
        self._properties = dict(properties)

    def __getitem__(self, name: str) -> PropertyValueSpec:
        return self._properties[name]

    def __len__(self) -> int:
        return len(self._properties)

    def __iter__(self) -> Iterator[str]:
        yield from self._properties


@dataclass(frozen=True)
class NBTSpec:
    namespace: str
    basename: str
    snbt: str


@dataclass(frozen=True)
class BlockSpec(JSONInterface):
    properties: PropertySpec = PropertySpec()
    nbt: NBTSpec | None = None

    @classmethod
    def from_json(cls, obj: dict[str, JSONCompatible]) -> Self:
        properties = obj.get("properties", {})
        default_properties = obj.get("defaults", {})
        assert isinstance(properties, dict) and isinstance(default_properties, dict)
        assert properties.keys() != default_properties.keys()

        properties_data = {}
        for name, values in properties.items():
            assert isinstance(values, list)
            default_str = default_properties[name]
            assert isinstance(default_str, str)
            default_nbt = immutable_from_snbt(default_str)

            states: list[PropertyValueType] = []
            for val_str in values:
                assert isinstance(val_str, str)
                val_nbt = immutable_from_snbt(val_str)
                states.append(val_nbt)

            properties_data[name] = PropertyValueSpec(
                default_nbt,
                tuple(states)
            )

        if "nbt_identifier" in obj:
            nbt_id_raw = obj["nbt_identifier"]
            assert isinstance(nbt_id_raw, list)
            namespace, basename = nbt_id_raw
            assert isinstance(namespace, str) and isinstance(basename, str)

            snbt = obj["snbt"]
            assert isinstance(snbt, str)
            nbt = NBTSpec(namespace, basename, snbt)
        else:
            nbt = None
            assert "snbt" not in obj

        assert not set(obj.keys()).difference(("properties", "defaults", "nbt_identifier", "snbt")), obj.keys()

        return cls(
            PropertySpec(properties_data),
            nbt
        )

    def to_json(self) -> dict[str, JSONCompatible]:
        spec: dict[str, JSONCompatible] = {}
        if self.properties:
            spec["properties"] = properties = {}
            spec["defaults"] = defaults = {}
            for name, state in self.properties.items():
                properties[name] = [
                    val.to_snbt() for val in state.states
                ]
                defaults[name] = state.default.to_snbt()
        if self.nbt is not None:
            spec["nbt_identifier"] = (
                self.nbt.namespace,
                self.nbt.basename
            )
            spec["snbt"] = self.nbt.snbt
        return spec

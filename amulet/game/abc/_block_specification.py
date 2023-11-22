from typing import Self
from collections.abc import Mapping, Iterator
from dataclasses import dataclass

from amulet_nbt import CompoundTag, from_snbt
from amulet.block import PropertyValueType, PropertyDataTypes

from ._json_interface import JSONInterface, JSONCompatible


def immutable_from_snbt(snbt: str) -> PropertyValueType:
    val = from_snbt(snbt)
    if not isinstance(val, PropertyDataTypes):
        raise TypeError
    return val


@dataclass(frozen=True)
class PropertiesState:
    default: PropertyValueType
    states: tuple[PropertyValueType, ...]


class PropertiesData(Mapping[str, PropertiesState]):
    def __init__(self, properties: dict[str, PropertiesState]):
        self._properties = properties

    def __getitem__(self, name: str) -> PropertiesState:
        return self._properties[name]

    def __len__(self) -> int:
        return len(self._properties)

    def __iter__(self) -> Iterator[str]:
        yield from self._properties


class BlockSpecification(JSONInterface):
    def __init__(
        self,
        properties: PropertiesData,
        nbt_id: tuple[str, str] | None,
        snbt: str | None
    ):
        self._properties = properties
        self._nbt_id = nbt_id
        self._snbt = snbt

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

            properties_data[name] = PropertiesState(
                default_nbt,
                tuple(states)
            )

        nbt_id_raw = obj.get("nbt_identifier", None)
        if nbt_id_raw is None:
            nbt_id = None
        else:
            assert isinstance(nbt_id_raw, list)
            namespace, basename = nbt_id_raw
            assert isinstance(namespace, str) and isinstance(basename, str)
            nbt_id = (namespace, basename)

        snbt = obj.get("snbt", None)
        assert snbt is None or isinstance(snbt, str)

        return cls(
            PropertiesData(properties_data),
            nbt_id,
            snbt,
        )

    def to_json(self) -> dict[str, JSONCompatible]:
        spec: dict[str, JSONCompatible] = {}
        if self._properties:
            spec["properties"] = properties = {}
            spec["defaults"] = defaults = {}
            for name, state in self._properties.items():
                properties[name] = [
                    val.to_snbt() for val in state.states
                ]
                defaults[name] = state.default.to_snbt()
        if self._nbt_id is not None:
            spec["nbt_identifier"] = self._nbt_id
        if self._snbt is not None:
            spec["snbt"] = self._snbt
        return spec

    @property
    def properties(self) -> PropertiesData:
        return self._properties

    @property
    def nbt_id(self) -> tuple[str, str] | None:
        return self._nbt_id

    @property
    def default_nbt(self) -> CompoundTag | None:
        if self._snbt is None:
            return None
        else:
            tag = from_snbt(self._snbt)
            if isinstance(tag, CompoundTag):
                return tag
            raise TypeError

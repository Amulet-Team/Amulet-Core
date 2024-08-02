from typing import Self
from types import MappingProxyType
from collections.abc import Mapping, Iterator, Hashable
from dataclasses import dataclass, field
import os
import json
import glob
from concurrent.futures import ThreadPoolExecutor

from amulet_nbt import read_snbt
from amulet.block import PropertyValueType

from .json_interface import JSONInterface, JSONDict, JSONCompatible


def immutable_from_snbt(snbt: str) -> PropertyValueType:
    val = read_snbt(snbt)
    assert isinstance(val, PropertyValueType)
    return val


@dataclass(frozen=True)
class PropertyValueSpec:
    default: PropertyValueType
    states: tuple[PropertyValueType, ...]


class PropertySpec(Mapping[str, PropertyValueSpec], Hashable):
    _properties: Mapping[str, PropertyValueSpec]
    _hash: int | None

    def __init__(
        self, properties: Mapping[str, PropertyValueSpec] = MappingProxyType({})
    ):
        self._properties = dict(properties)
        self._hash = None

    def __getitem__(self, name: str) -> PropertyValueSpec:
        return self._properties[name]

    def __len__(self) -> int:
        return len(self._properties)

    def __iter__(self) -> Iterator[str]:
        yield from self._properties

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self._properties.items()))
        return self._hash


@dataclass(frozen=True)
class NBTSpec:
    namespace: str
    base_name: str
    snbt: str


@dataclass(frozen=True)
class BlockSpec(JSONInterface):
    properties: PropertySpec = field(default_factory=PropertySpec)
    nbt: NBTSpec | None = None

    @classmethod
    def from_json(cls, obj: JSONCompatible) -> Self:
        assert isinstance(obj, dict)
        properties = obj.get("properties", {})
        default_properties = obj.get("defaults", {})
        assert isinstance(properties, dict) and isinstance(default_properties, dict)
        assert properties.keys() == default_properties.keys()

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

            properties_data[name] = PropertyValueSpec(default_nbt, tuple(states))

        if "nbt_identifier" in obj:
            nbt_id_raw = obj["nbt_identifier"]
            assert isinstance(nbt_id_raw, list)
            namespace, base_name = nbt_id_raw
            assert isinstance(namespace, str) and isinstance(base_name, str)

            snbt = obj["snbt"]
            assert isinstance(snbt, str)
            nbt = NBTSpec(namespace, base_name, snbt)
        else:
            nbt = None
            assert "snbt" not in obj

        assert not set(obj.keys()).difference(
            ("properties", "defaults", "nbt_identifier", "snbt")
        ), obj.keys()

        return cls(PropertySpec(properties_data), nbt)

    def to_json(self) -> JSONDict:
        spec: JSONDict = {}
        if self.properties:
            spec["properties"] = properties = {}
            spec["defaults"] = defaults = {}
            for name, state in self.properties.items():
                properties[name] = [val.to_snbt() for val in state.states]
                defaults[name] = state.default.to_snbt()
        if self.nbt is not None:
            spec["nbt_identifier"] = [self.nbt.namespace, self.nbt.base_name]
            spec["snbt"] = self.nbt.snbt
        return spec


def _read_glob(path: str) -> str:
    with open(path) as f:
        return f.read()


def load_json_block_spec(
    version_path: str, block_format: str
) -> dict[str, dict[str, BlockSpec]]:
    """Load all block specification files for the given version."""
    block_spec = dict[str, dict[str, BlockSpec]]()
    paths = glob.glob(
        os.path.join(
            glob.escape(version_path),
            "block",
            block_format,
            "specification",
            "*",
            "*",
            "*.json",
        )
    )
    with ThreadPoolExecutor() as e:
        for file_path, data in zip(paths, e.map(_read_glob, paths)):
            *_, namespace, _, base_name = os.path.splitext(os.path.normpath(file_path))[
                0
            ].split(os.sep)
            block_spec.setdefault(namespace, {})[base_name] = BlockSpec.from_json(
                json.loads(data)
            )
    return block_spec

from collections.abc import Hashable, Iterator, Mapping
from dataclasses import dataclass
from typing import Self

from amulet.block import PropertyValueType as PropertyValueType

from .json_interface import JSONCompatible as JSONCompatible
from .json_interface import JSONDict as JSONDict
from .json_interface import JSONInterface as JSONInterface

def immutable_from_snbt(snbt: str) -> PropertyValueType: ...
@dataclass(frozen=True)
class PropertyValueSpec:
    default: PropertyValueType
    states: tuple[PropertyValueType, ...]
    def __init__(self, default, states) -> None: ...

class PropertySpec(Mapping[str, PropertyValueSpec], Hashable):
    def __init__(self, properties: Mapping[str, PropertyValueSpec] = ...) -> None: ...
    def __getitem__(self, name: str) -> PropertyValueSpec: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[str]: ...
    def __hash__(self) -> int: ...

@dataclass(frozen=True)
class NBTSpec:
    namespace: str
    base_name: str
    snbt: str
    def __init__(self, namespace, base_name, snbt) -> None: ...

@dataclass(frozen=True)
class BlockSpec(JSONInterface):
    properties: PropertySpec = ...
    nbt: NBTSpec | None = ...
    @classmethod
    def from_json(cls, obj: JSONCompatible) -> Self: ...
    def to_json(self) -> JSONDict: ...
    def __init__(self, properties=..., nbt=...) -> None: ...

def load_json_block_spec(
    version_path: str, block_format: str
) -> dict[str, dict[str, BlockSpec]]:
    """Load all block specification files for the given version."""

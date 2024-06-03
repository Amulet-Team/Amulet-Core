from __future__ import annotations

from typing import Union, Callable
from dataclasses import dataclass, field

from amulet_nbt import (
    NamedTag,
    ListTag,
    CompoundTag,
)

from amulet.block import Block, PropertyValueType
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.data_types import BlockCoordinates
from ._typing import NBTTagT, NBTPath


@dataclass(frozen=True)
class SrcDataExtra:
    absolute_coordinates: BlockCoordinates
    get_block_callback: Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]]


@dataclass(frozen=True)
class SrcData:
    block: Block | None
    nbt: NamedTag | None
    extra: SrcDataExtra | None


@dataclass
class StateData:
    relative_location: BlockCoordinates = (0, 0, 0)
    # nbt_path is only set when within walk_input_nbt
    nbt_path: tuple[str, type[ListTag] | type[CompoundTag], NBTPath] | None = None


@dataclass
class DstData:
    cls: type[Block] | type[Entity] | None = None
    resource_id: tuple[str, str] | None = None
    properties: dict[str, PropertyValueType] = field(default_factory=dict)
    nbt: list[
        tuple[
            str,
            type[ListTag] | type[CompoundTag],
            NBTPath,
            Union[str, int],
            NBTTagT,
        ]
    ] = field(default_factory=list)
    extra_needed: bool = False
    cacheable: bool = True

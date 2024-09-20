from dataclasses import dataclass
from typing import Callable

from amulet.block import Block as Block
from amulet.block import PropertyValueType as PropertyValueType
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.data_types import BlockCoordinates as BlockCoordinates
from amulet.entity import Entity as Entity
from amulet_nbt import CompoundTag, ListTag
from amulet_nbt import NamedTag as NamedTag

from ._typing import NBTPath as NBTPath
from ._typing import NBTTagT as NBTTagT

@dataclass(frozen=True)
class SrcDataExtra:
    absolute_coordinates: BlockCoordinates
    get_block_callback: Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]]
    def __init__(self, absolute_coordinates, get_block_callback) -> None: ...

@dataclass(frozen=True)
class SrcData:
    block: Block | None
    nbt: NamedTag | None
    extra: SrcDataExtra | None
    def __init__(self, block, nbt, extra) -> None: ...

@dataclass
class StateData:
    relative_location: BlockCoordinates = ...
    nbt_path: tuple[str, type[ListTag] | type[CompoundTag], NBTPath] | None = ...
    def __init__(self, relative_location=..., nbt_path=...) -> None: ...

@dataclass
class DstData:
    cls: type[Block] | type[Entity] | None = ...
    resource_id: tuple[str, str] | None = ...
    properties: dict[str, PropertyValueType] = ...
    nbt: list[
        tuple[str, type[ListTag] | type[CompoundTag], NBTPath, str | int, NBTTagT]
    ] = ...
    extra_needed: bool = ...
    cacheable: bool = ...
    def __init__(
        self,
        cls=...,
        resource_id=...,
        properties=...,
        nbt=...,
        extra_needed=...,
        cacheable=...,
    ) -> None: ...

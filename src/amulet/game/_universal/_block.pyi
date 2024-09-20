from typing import Callable

from amulet.block import Block as Block
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.data_types import BlockCoordinates as BlockCoordinates
from amulet.entity import Entity as Entity
from amulet.game.abc import BlockData as BlockData
from amulet.version import VersionNumber as VersionNumber

class UniversalBlockData(BlockData):
    def to_universal(
        self,
        block: Block,
        block_entity: BlockEntity | None,
        extra: (
            tuple[
                BlockCoordinates,
                Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
            ]
            | None
        ),
    ) -> tuple[Block, BlockEntity | None, bool]: ...
    def from_universal(
        self,
        target_platform: str,
        target_version: VersionNumber,
        block: Block,
        block_entity: BlockEntity | None,
        extra: (
            tuple[
                BlockCoordinates,
                Callable[[BlockCoordinates], tuple[Block, BlockEntity | None]],
            ]
            | None
        ),
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]: ...

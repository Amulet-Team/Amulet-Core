from typing import Callable

from amulet.data_types import BlockCoordinates
from amulet.block import Block
from amulet.block_entity import BlockEntity
from amulet.entity import Entity

from amulet.game.abc import BlockData
from amulet.version import VersionNumber


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
    ) -> tuple[Block, BlockEntity | None, bool]:
        # Converting universal to universal so just return as is
        if not self._game_version.supports_version(block.platform, block.version):
            raise ValueError("The block is not compatible with this version")
        return block, block_entity, False

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
    ) -> tuple[Block, BlockEntity | None, bool] | tuple[Entity, None, bool]:
        # Converting universal to universal so just return as is
        if not self._game_version.supports_version(block.platform, block.version):
            raise ValueError("The block is not compatible with this version")
        return block, block_entity, False

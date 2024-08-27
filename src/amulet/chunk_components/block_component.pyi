from __future__ import annotations
import amulet.block
import amulet.chunk_components.section_array_map
import amulet.palette.block_palette
import amulet.version
import typing

__all__ = ["BlockComponent", "BlockComponentData"]

class BlockComponent:
    ComponentID: typing.ClassVar[str] = "Amulet::BlockComponent"
    block: BlockComponentData

class BlockComponentData:
    def __init__(
        self,
        version_range: amulet.version.VersionRange,
        array_shape: tuple[int, int, int],
        default_block: amulet.block.BlockStack,
    ) -> None: ...
    @property
    def palette(self) -> amulet.palette.block_palette.BlockPalette: ...
    @property
    def sections(self) -> amulet.chunk_components.section_array_map.SectionArrayMap: ...

from __future__ import annotations

import amulet.biome
import amulet.block
import amulet.level.abc.chunk_handle

__all__ = ["Dimension"]

class Dimension:
    def default_biome(self) -> amulet.biome.Biome: ...
    def default_block(self) -> amulet.block.BlockStack: ...
    def get_chunk_handle(
        self, cx: int, cz: int
    ) -> amulet.level.abc.chunk_handle.ChunkHandle: ...
    @property
    def dimension_id(self) -> str: ...

from __future__ import annotations

import amulet.biome
import amulet.block
import amulet.level.abc.chunk_handle

__all__ = ["Dimension"]

class Dimension:
    def default_biome(self) -> amulet.biome.Biome:
        """
        The default biome for this dimension
        """

    def default_block(self) -> amulet.block.BlockStack:
        """
        The default block for this dimension
        """

    def get_chunk_handle(
        self, cx: int, cz: int
    ) -> amulet.level.abc.chunk_handle.ChunkHandle:
        """
        Get the chunk handle for the given chunk in this dimension.

        :param cx: The chunk x coordinate to load.
        :param cz: The chunk z coordinate to load.
        """

    @property
    def dimension_id(self) -> str:
        """
        The dimension identifier this chunk is from.
        """

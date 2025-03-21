from __future__ import annotations

import amulet.biome
import amulet.block
import amulet.level.abc.chunk_handle

__all__ = ["Dimension"]

class Dimension:
    def default_biome(self) -> amulet.biome.Biome:
        """
        The default biome for this dimension
        Thread safe.
        """

    def default_block(self) -> amulet.block.BlockStack:
        """
        The default block for this dimension.
        Thread safe.
        """

    def get_chunk_handle(
        self, cx: int, cz: int
    ) -> amulet.level.abc.chunk_handle.ChunkHandle:
        """
        Get the chunk handle for the given chunk in this dimension.
        Thread safe.

        :param cx: The chunk x coordinate to load.
        :param cz: The chunk z coordinate to load.
        """

    @property
    def bounds(self) -> ...:
        """
        The editable region of the dimension.
        Thread safe.
        """

    @property
    def dimension_id(self) -> str:
        """
        Get the dimension id for this dimension.
        Thread safe.
        """

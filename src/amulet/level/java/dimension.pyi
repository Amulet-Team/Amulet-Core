from __future__ import annotations

from builtins import str as JavaInternalDimensionID

import amulet.level.abc.dimension
import amulet.level.java.chunk_handle

__all__ = ["JavaDimension", "JavaInternalDimensionID"]

class JavaDimension(amulet.level.abc.dimension.Dimension):
    def get_chunk_handle(
        self, cx: int, cz: int
    ) -> amulet.level.java.chunk_handle.JavaChunkHandle:
        """
        Get the chunk handle for the given chunk in this dimension.
        Thread safe.

        :param cx: The chunk x coordinate to load.
        :param cz: The chunk z coordinate to load.
        """

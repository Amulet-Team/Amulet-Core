from __future__ import annotations

import amulet.level.abc.chunk_handle
import amulet.level.java.chunk

__all__ = ["JavaChunkHandle"]

class JavaChunkHandle(amulet.level.abc.chunk_handle.ChunkHandle):
    def get_chunk(self) -> amulet.level.java.chunk.JavaChunk:
        """
        Get a unique copy of the chunk data.
        """

    def set_chunk(self, chunk: amulet.level.java.chunk.JavaChunk) -> None:
        """
        Overwrite the chunk data.
        """

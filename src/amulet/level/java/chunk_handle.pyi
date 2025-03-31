from __future__ import annotations

import typing

import amulet.chunk
import amulet.level.abc.chunk_handle
import amulet.level.java.chunk

__all__ = ["JavaChunkHandle"]

class JavaChunkHandle(amulet.level.abc.chunk_handle.ChunkHandle):
    def get_chunk(self) -> amulet.level.java.chunk.JavaChunk:
        """
        Get a unique copy of the chunk data.
        """

    @typing.overload
    def set_chunk(self, chunk: amulet.level.java.chunk.JavaChunk) -> None:
        """
        Overwrite the chunk data.
        You must acquire the chunk lock before setting.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        """

    @typing.overload
    def set_chunk(self, chunk: amulet.chunk.Chunk) -> None:
        """
        Overwrite the chunk data.
        You must acquire the chunk lock before setting.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        """

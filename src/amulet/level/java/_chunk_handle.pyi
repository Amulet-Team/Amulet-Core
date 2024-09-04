from __future__ import annotations
import amulet.level.abc._chunk_handle
from amulet.level.abc._chunk_handle import ChunkHandle
from amulet.level.java.chunk import JavaChunk
import typing

__all__ = ["ChunkHandle", "ChunkT", "JavaChunk", "JavaChunkHandle"]

class JavaChunkHandle(amulet.level.abc._chunk_handle.ChunkHandle):
    @staticmethod
    def _validate_chunk(chunk: ChunkT) -> None: ...

ChunkT: typing.TypeVar  # value = ~ChunkT

from __future__ import annotations

from amulet.level.abc import ChunkHandle
from amulet.chunk import Chunk
from .chunk import BedrockChunk


class BedrockChunkHandle(ChunkHandle):
    @staticmethod
    def _validate_chunk(chunk: Chunk) -> None:
        if not isinstance(chunk, BedrockChunk):
            raise TypeError

from __future__ import annotations
from typing import TYPE_CHECKING

from amulet.level.abc import ChunkHandle
from ..abc._chunk_handle import ChunkT
from .chunk import BedrockChunk

if TYPE_CHECKING:
    from ._level import BedrockLevel
    from ._raw import BedrockRawDimension


class BedrockChunkHandle(
    ChunkHandle["BedrockLevel", "BedrockRawDimension", BedrockChunk]
):
    @staticmethod
    def _validate_chunk(chunk: ChunkT) -> None:
        if not isinstance(chunk, BedrockChunk):
            raise TypeError

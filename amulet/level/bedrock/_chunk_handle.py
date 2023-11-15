from typing import TYPE_CHECKING

from amulet.level.abc import ChunkHandle
from ..abc._chunk_handle import ChunkT

if TYPE_CHECKING:
    from ._level import BedrockLevel
    from ._raw import BedrockRawDimension
    from .chunk import BedrockChunk


class BedrockChunkHandle(ChunkHandle[BedrockLevel, BedrockRawDimension, BedrockChunk]):
    def _validate_chunk(self, chunk: ChunkT) -> None:
        if not isinstance(chunk, BedrockChunk):
            raise TypeError

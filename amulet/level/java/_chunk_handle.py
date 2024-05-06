from __future__ import annotations
from typing import TYPE_CHECKING

from amulet.level.abc import ChunkHandle
from ..abc._chunk_handle import ChunkT
from .chunk import JavaChunk

if TYPE_CHECKING:
    from ._level import JavaLevel
    from ._raw import JavaRawDimension


class JavaChunkHandle(ChunkHandle["JavaLevel", "JavaRawDimension", JavaChunk]):
    @staticmethod
    def _validate_chunk(chunk: ChunkT) -> None:
        if not isinstance(chunk, JavaChunk):
            raise TypeError

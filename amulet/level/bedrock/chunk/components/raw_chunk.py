from __future__ import annotations
from amulet.level.bedrock._raw import BedrockRawChunk
from amulet.chunk.components.abc import ChunkComponent


class RawChunkComponent(ChunkComponent[BedrockRawChunk | None, BedrockRawChunk | None]):
    storage_key = b"brc"

    @staticmethod
    def fix_set_data(
        old_obj: BedrockRawChunk | None, new_obj: BedrockRawChunk | None
    ) -> BedrockRawChunk | None:
        if new_obj is None or isinstance(new_obj, BedrockRawChunk):
            return new_obj
        raise TypeError

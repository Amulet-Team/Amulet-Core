from __future__ import annotations
from amulet_nbt import NamedTag
from amulet.chunk.components.abc import ChunkComponent
from amulet.level.java.anvil import RawChunkType


class RawChunkComponent(ChunkComponent[RawChunkType | None, RawChunkType | None]):
    storage_key = b"jrc"

    @staticmethod
    def fix_set_data(old_obj: RawChunkType | None, new_obj: RawChunkType | None) -> RawChunkType | None:
        if new_obj is None or (isinstance(new_obj, dict) and all(isinstance(key, str) and isinstance(value, NamedTag) for key, value in new_obj.items())):
            return new_obj
        raise TypeError

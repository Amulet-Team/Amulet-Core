from __future__ import annotations
from amulet.chunk.components.abc import ChunkComponent


class InhabitedTimeComponent(ChunkComponent[int, int]):
    storage_key = b"jit"

    @staticmethod
    def fix_set_data(old_obj: int, new_obj: int) -> int:
        if not isinstance(new_obj, int):
            raise TypeError
        return new_obj

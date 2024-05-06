from __future__ import annotations
from amulet.chunk.components.abc import ChunkComponent


class DataVersionComponent(ChunkComponent[int, int]):
    storage_key = b"jdv"

    @staticmethod
    def fix_set_data(old_obj: int, new_obj: int) -> int:
        if not isinstance(new_obj, int):
            raise TypeError
        if old_obj != new_obj:
            raise RuntimeError("The data version cannot be changed.")
        return new_obj

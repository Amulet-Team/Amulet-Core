from __future__ import annotations
import struct

from .leveldb_25 import (
    LevelDB25Interface,
)


class LevelDB29Interface(LevelDB25Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 29)

    @staticmethod
    def _get_sub_chunk_storage_byte(cy: int, min_y: int) -> bytes:
        return struct.pack("b", cy)


export = LevelDB29Interface

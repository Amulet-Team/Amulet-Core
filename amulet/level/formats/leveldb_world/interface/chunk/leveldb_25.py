from __future__ import annotations
import struct

from .leveldb_24 import (
    LevelDB24Interface as ParentInterface,
)


class LevelDB25Interface(ParentInterface):
    chunk_version = 25

    @staticmethod
    def _chunk_key_to_sub_chunk(cy: int, min_y: int) -> int:
        return cy + min_y

    @staticmethod
    def _get_sub_chunk_storage_byte(cy: int, min_y: int) -> bytes:
        # The chunk db keys all start at 0 regardless of chunk floor position.
        # This is the floor position of when the world was created.
        # If the floor position changes in the future this will break.
        return struct.pack("b", cy - min_y)


export = LevelDB25Interface

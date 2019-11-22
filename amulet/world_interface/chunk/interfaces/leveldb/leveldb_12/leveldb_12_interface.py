from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_11.leveldb_11_interface import (
    LevelDB11Interface
)


class LevelDB12Interface(LevelDB11Interface):
    def __init__(self):
        LevelDB11Interface.__init__(self)

        self.features["chunk_version"] = 12

    @staticmethod
    def is_valid(key):
        if key[0] != "leveldb":
            return False
        if key[1] != 12:
            return False
        return True


INTERFACE_CLASS = LevelDB12Interface

from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_10.leveldb_10_interface import (
    LevelDB10Interface,
)


class LevelDB11Interface(LevelDB10Interface):
    def __init__(self):
        LevelDB10Interface.__init__(self)

        self.features["chunk_version"] = 11

    @staticmethod
    def is_valid(key):
        if key[0] != "bedrock":
            return False
        if key[1] != 11:
            return False
        return True


INTERFACE_CLASS = LevelDB11Interface

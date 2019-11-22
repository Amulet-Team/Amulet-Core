from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_12.leveldb_12_interface import (
    LevelDB12Interface
)


class LevelDB13Interface(LevelDB12Interface):
    def __init__(self):
        LevelDB12Interface.__init__(self)

        self.features["chunk_version"] = 13

    @staticmethod
    def is_valid(key):
        if key[0] != "leveldb":
            return False
        if key[1] != 13:
            return False
        return True


INTERFACE_CLASS = LevelDB13Interface

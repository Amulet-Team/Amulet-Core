from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_14.leveldb_14_interface import LevelDB14Interface


class LevelDB15Interface(LevelDB14Interface):
    def __init__(self):
        LevelDB14Interface.__init__(self)

        self.features["chunk_version"] = 15

    @staticmethod
    def is_valid(key):
        if key[0] != "leveldb":
            return False
        if key[1] != 15:
            return False
        return True


INTERFACE_CLASS = LevelDB15Interface

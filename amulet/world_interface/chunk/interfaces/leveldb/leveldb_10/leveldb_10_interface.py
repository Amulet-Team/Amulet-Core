from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.base_leveldb_interface import BaseLevelDBInterface


class LevelDB10Interface(BaseLevelDBInterface):
    def __init__(self):
        BaseLevelDBInterface.__init__(self)

        self.features["chunk_version"] = 10
        self.features["finalised_state"] = "int0-2"
        # self.features["data_2d"] =
        self.features["entities"] = "32list"
        self.features["block_entities"] = "31list"
        self.features["terrain"] = "2fnpalette"

    @staticmethod
    def is_valid(key):
        if key[0] != "leveldb":
            return False
        if key[1] != 10:
            return False
        return True


INTERFACE_CLASS = LevelDB10Interface

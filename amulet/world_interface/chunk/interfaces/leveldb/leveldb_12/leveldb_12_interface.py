from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_11.leveldb_11_interface import (
    LevelDB11Interface,
)


class LevelDB12Interface(LevelDB11Interface):
    def __init__(self):
        LevelDB11Interface.__init__(self)

        self.features["chunk_version"] = 12


INTERFACE_CLASS = LevelDB12Interface

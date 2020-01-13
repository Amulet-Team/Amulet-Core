from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_14.leveldb_14_interface import (
    LevelDB14Interface,
)


class LevelDB15Interface(LevelDB14Interface):
    def __init__(self):
        LevelDB14Interface.__init__(self)

        self.features["chunk_version"] = 15


INTERFACE_CLASS = LevelDB15Interface

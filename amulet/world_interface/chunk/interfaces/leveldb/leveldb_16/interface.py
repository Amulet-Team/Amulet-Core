from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_15.interface import (
    LevelDB15Interface
)


class LevelDB16Interface(LevelDB15Interface):
    def __init__(self):
        LevelDB15Interface.__init__(self)

        self.features["chunk_version"] = 16


INTERFACE_CLASS = LevelDB16Interface

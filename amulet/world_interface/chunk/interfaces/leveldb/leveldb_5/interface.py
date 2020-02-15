from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_4.interface import (
    LevelDB4Interface
)


class LevelDB5Interface(LevelDB4Interface):
    def __init__(self):
        LevelDB4Interface.__init__(self)

        self.features["chunk_version"] = 5


INTERFACE_CLASS = LevelDB5Interface

from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_3.interface import (
    LevelDB3Interface,
)


class LevelDB4Interface(LevelDB3Interface):
    def __init__(self):
        LevelDB3Interface.__init__(self)

        self.features["chunk_version"] = 4


INTERFACE_CLASS = LevelDB4Interface

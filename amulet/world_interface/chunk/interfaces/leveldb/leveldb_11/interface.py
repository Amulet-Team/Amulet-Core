from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_10.interface import (
    LevelDB10Interface,
)


class LevelDB11Interface(LevelDB10Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 11


INTERFACE_CLASS = LevelDB11Interface

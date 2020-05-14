from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_6.interface import (
    LevelDB6Interface,
)


class LevelDB7Interface(LevelDB6Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 7


INTERFACE_CLASS = LevelDB7Interface

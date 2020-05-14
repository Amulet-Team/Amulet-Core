from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_7.interface import (
    LevelDB7Interface,
)


class LevelDB8Interface(LevelDB7Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 8
        self.features["terrain"] = "2fnpalette"


INTERFACE_CLASS = LevelDB8Interface

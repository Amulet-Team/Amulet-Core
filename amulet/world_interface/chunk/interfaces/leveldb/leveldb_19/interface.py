from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_18.interface import (
    LevelDB18Interface,
)


class LevelDB19Interface(LevelDB18Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 19


INTERFACE_CLASS = LevelDB19Interface

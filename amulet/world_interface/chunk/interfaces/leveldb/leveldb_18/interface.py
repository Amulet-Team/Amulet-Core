from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_17.interface import (
    LevelDB17Interface,
)


class LevelDB18Interface(LevelDB17Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 18


INTERFACE_CLASS = LevelDB18Interface

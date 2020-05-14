from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_5.interface import (
    LevelDB5Interface,
)


class LevelDB6Interface(LevelDB5Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 6


INTERFACE_CLASS = LevelDB6Interface

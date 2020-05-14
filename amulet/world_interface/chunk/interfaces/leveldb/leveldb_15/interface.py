from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_14.interface import (
    LevelDB14Interface,
)


class LevelDB15Interface(LevelDB14Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 15


INTERFACE_CLASS = LevelDB15Interface

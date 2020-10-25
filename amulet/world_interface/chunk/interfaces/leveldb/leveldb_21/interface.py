from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_20.interface import (
    LevelDB20Interface,
)


class LevelDB21Interface(LevelDB20Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 21


INTERFACE_CLASS = LevelDB21Interface

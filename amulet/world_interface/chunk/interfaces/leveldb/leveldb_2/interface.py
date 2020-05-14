from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_1.interface import (
    LevelDB1Interface,
)


class LevelDB2Interface(LevelDB1Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 2


INTERFACE_CLASS = LevelDB2Interface

from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_16.interface import (
    LevelDB16Interface,
)


class LevelDB17Interface(LevelDB16Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 17


INTERFACE_CLASS = LevelDB17Interface

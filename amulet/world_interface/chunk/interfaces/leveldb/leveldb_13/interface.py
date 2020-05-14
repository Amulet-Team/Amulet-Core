from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_12.interface import (
    LevelDB12Interface,
)


class LevelDB13Interface(LevelDB12Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 13


INTERFACE_CLASS = LevelDB13Interface

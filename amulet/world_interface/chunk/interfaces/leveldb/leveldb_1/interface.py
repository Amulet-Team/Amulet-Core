from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_0.interface import (
    LevelDB0Interface,
)


class LevelDB1Interface(LevelDB0Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 1


INTERFACE_CLASS = LevelDB1Interface

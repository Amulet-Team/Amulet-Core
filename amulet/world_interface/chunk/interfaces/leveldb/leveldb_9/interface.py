from __future__ import annotations

from amulet.world_interface.chunk.interfaces.leveldb.leveldb_8.interface import (
    LevelDB8Interface,
)


class LevelDB9Interface(LevelDB8Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 9
        self.features[
            "entity_format"
        ] = "namespace-str-identifier"  # "int-id" is present until at least v7. Not sure which was present for v8


INTERFACE_CLASS = LevelDB9Interface

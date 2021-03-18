# meta interface
from __future__ import annotations

from amulet.api.wrapper import EntityIDType
from .leveldb_8 import (
    LevelDB8Interface,
)


class LevelDB9Interface(LevelDB8Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 9
        self.features[
            "entity_format"
        ] = (
            EntityIDType.namespace_str_identifier
        )  # EntityIDType.int_id is present until at least v7. Not sure which was present for v8


export = LevelDB9Interface

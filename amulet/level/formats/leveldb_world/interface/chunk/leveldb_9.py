from __future__ import annotations

from amulet.api.wrapper import EntityIDType
from .leveldb_8 import (
    LevelDB8Interface,
)


class LevelDB9Interface(LevelDB8Interface):

    chunk_version = 9

    def __init__(self):
        super().__init__()
        # EntityIDType.int_id is present until at least v7. Not sure which was present for v8
        self._set_feature("entity_format", EntityIDType.namespace_str_identifier)


export = LevelDB9Interface

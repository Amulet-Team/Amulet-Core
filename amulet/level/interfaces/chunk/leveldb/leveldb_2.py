from __future__ import annotations

from .leveldb_1 import (
    LevelDB1Interface,
)


class LevelDB2Interface(LevelDB1Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 2)


export = LevelDB2Interface

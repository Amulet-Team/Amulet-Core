from __future__ import annotations

from .leveldb_14 import (
    LevelDB14Interface,
)


class LevelDB15Interface(LevelDB14Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 15)


export = LevelDB15Interface

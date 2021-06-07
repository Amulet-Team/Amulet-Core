from __future__ import annotations

from .leveldb_7 import (
    LevelDB7Interface,
)


class LevelDB8Interface(LevelDB7Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 8)
        self._set_feature("terrain", "2fnpalette")


export = LevelDB8Interface

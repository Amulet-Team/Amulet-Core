from __future__ import annotations

from .leveldb_2 import (
    LevelDB2Interface,
)


class LevelDB3Interface(LevelDB2Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 3)
        self._set_feature("terrain", "2farray")


export = LevelDB3Interface

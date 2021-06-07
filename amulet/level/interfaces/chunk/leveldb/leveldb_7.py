from __future__ import annotations

from .leveldb_6 import (
    LevelDB6Interface,
)


class LevelDB7Interface(LevelDB6Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 7)


export = LevelDB7Interface

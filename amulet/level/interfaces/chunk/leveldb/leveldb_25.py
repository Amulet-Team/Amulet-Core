from __future__ import annotations

from .leveldb_22 import (
    LevelDB22Interface,
)


class LevelDB25Interface(LevelDB22Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 25)


export = LevelDB25Interface

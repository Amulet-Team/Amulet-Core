from __future__ import annotations

from .leveldb_18 import (
    LevelDB18Interface,
)


class LevelDB19Interface(LevelDB18Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 19)


export = LevelDB19Interface

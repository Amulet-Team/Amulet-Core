from __future__ import annotations

from .leveldb_17 import (
    LevelDB17Interface,
)


class LevelDB18Interface(LevelDB17Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 18)


export = LevelDB18Interface

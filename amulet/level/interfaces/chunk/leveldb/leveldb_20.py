from __future__ import annotations

from .leveldb_19 import (
    LevelDB19Interface,
)


class LevelDB20Interface(LevelDB19Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 20)


export = LevelDB20Interface

from __future__ import annotations

from .leveldb_5 import (
    LevelDB5Interface,
)


class LevelDB6Interface(LevelDB5Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 6)


export = LevelDB6Interface

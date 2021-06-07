from __future__ import annotations

from .leveldb_4 import (
    LevelDB4Interface,
)


class LevelDB5Interface(LevelDB4Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 5)


export = LevelDB5Interface

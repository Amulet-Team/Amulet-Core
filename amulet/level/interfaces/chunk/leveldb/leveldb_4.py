from __future__ import annotations

from .leveldb_3 import (
    LevelDB3Interface,
)


class LevelDB4Interface(LevelDB3Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 4)


export = LevelDB4Interface

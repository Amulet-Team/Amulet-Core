from __future__ import annotations

from .leveldb_25 import (
    LevelDB25Interface,
)


class LevelDB26Interface(LevelDB25Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 26)


export = LevelDB26Interface

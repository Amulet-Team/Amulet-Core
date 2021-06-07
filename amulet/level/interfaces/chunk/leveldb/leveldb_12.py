from __future__ import annotations

from .leveldb_11 import (
    LevelDB11Interface,
)


class LevelDB12Interface(LevelDB11Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 12)


export = LevelDB12Interface

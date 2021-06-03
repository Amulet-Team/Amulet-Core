from __future__ import annotations

from .leveldb_16 import (
    LevelDB16Interface,
)


class LevelDB17Interface(LevelDB16Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 17)


export = LevelDB17Interface

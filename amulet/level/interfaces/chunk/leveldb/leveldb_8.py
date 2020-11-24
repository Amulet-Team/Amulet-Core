# meta interface
from __future__ import annotations

from .leveldb_7 import (
    LevelDB7Interface,
)


class LevelDB8Interface(LevelDB7Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 8
        self.features["terrain"] = "2fnpalette"


export = LevelDB8Interface

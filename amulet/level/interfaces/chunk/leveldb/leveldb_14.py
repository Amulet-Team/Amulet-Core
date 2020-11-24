# meta interface
from __future__ import annotations

from .leveldb_13 import (
    LevelDB13Interface,
)


class LevelDB14Interface(LevelDB13Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 14


INTERFACE_CLASS = LevelDB14Interface

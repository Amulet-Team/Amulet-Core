# meta interface
from __future__ import annotations

from .leveldb_14 import (
    LevelDB14Interface,
)


class LevelDB15Interface(LevelDB14Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 15


INTERFACE_CLASS = LevelDB15Interface

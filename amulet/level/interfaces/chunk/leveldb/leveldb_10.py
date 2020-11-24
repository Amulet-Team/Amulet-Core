# meta interface
from __future__ import annotations

from .leveldb_9 import (
    LevelDB9Interface,
)


class LevelDB10Interface(LevelDB9Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 10


export = LevelDB10Interface

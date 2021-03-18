from __future__ import annotations

from .leveldb_21 import (
    LevelDB21Interface,
)


class LevelDB22Interface(LevelDB21Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 22


export = LevelDB22Interface

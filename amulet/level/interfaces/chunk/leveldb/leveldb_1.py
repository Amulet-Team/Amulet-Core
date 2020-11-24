# meta interface
from __future__ import annotations

from .leveldb_0 import (
    LevelDB0Interface,
)


class LevelDB1Interface(LevelDB0Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 1


export = LevelDB1Interface

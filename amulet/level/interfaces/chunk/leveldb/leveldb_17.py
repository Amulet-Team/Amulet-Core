# meta interface
from __future__ import annotations

from .leveldb_16 import (
    LevelDB16Interface,
)


class LevelDB17Interface(LevelDB16Interface):
    def __init__(self):
        super().__init__()

        self.features["chunk_version"] = 17


INTERFACE_CLASS = LevelDB17Interface

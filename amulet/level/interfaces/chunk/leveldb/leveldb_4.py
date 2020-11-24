# meta interface
from __future__ import annotations

from .leveldb_3 import (
    LevelDB3Interface,
)


class LevelDB4Interface(LevelDB3Interface):
    def __init__(self):
        LevelDB3Interface.__init__(self)

        self.features["chunk_version"] = 4


export = LevelDB4Interface

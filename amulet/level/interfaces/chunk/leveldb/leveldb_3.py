# meta interface
from __future__ import annotations

from .leveldb_2 import (
    LevelDB2Interface,
)


class LevelDB3Interface(LevelDB2Interface):
    def __init__(self):
        LevelDB2Interface.__init__(self)

        self.features["chunk_version"] = 3

        self.features["terrain"] = "2farray"


INTERFACE_CLASS = LevelDB3Interface

from __future__ import annotations

from .leveldb_10 import (
    LevelDB10Interface,
)


class LevelDB11Interface(LevelDB10Interface):
    chunk_version = 11


export = LevelDB11Interface

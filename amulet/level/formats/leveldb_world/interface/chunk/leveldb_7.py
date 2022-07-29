from __future__ import annotations

from .leveldb_6 import (
    LevelDB6Interface,
)


class LevelDB7Interface(LevelDB6Interface):
    chunk_version = 7


export = LevelDB7Interface

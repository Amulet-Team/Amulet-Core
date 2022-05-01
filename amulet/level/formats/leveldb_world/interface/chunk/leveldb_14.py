from __future__ import annotations

from .leveldb_13 import (
    LevelDB13Interface,
)


class LevelDB14Interface(LevelDB13Interface):
    chunk_version = 14


export = LevelDB14Interface

from __future__ import annotations

from .leveldb_14 import (
    LevelDB14Interface,
)


class LevelDB15Interface(LevelDB14Interface):
    chunk_version = 15


export = LevelDB15Interface

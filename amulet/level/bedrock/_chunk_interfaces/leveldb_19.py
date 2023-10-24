from __future__ import annotations

from .leveldb_18 import (
    LevelDB18Interface,
)


class LevelDB19Interface(LevelDB18Interface):
    chunk_version = 19


export = LevelDB19Interface

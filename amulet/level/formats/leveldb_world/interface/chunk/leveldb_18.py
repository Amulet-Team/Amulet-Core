from __future__ import annotations

from .leveldb_17 import (
    LevelDB17Interface,
)


class LevelDB18Interface(LevelDB17Interface):
    chunk_version = 18


export = LevelDB18Interface

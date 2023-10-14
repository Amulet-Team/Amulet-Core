from __future__ import annotations

from .leveldb_9 import (
    LevelDB9Interface,
)


class LevelDB10Interface(LevelDB9Interface):
    chunk_version = 10


export = LevelDB10Interface

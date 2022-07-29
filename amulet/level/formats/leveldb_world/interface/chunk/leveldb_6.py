from __future__ import annotations

from .leveldb_5 import (
    LevelDB5Interface,
)


class LevelDB6Interface(LevelDB5Interface):
    chunk_version = 6


export = LevelDB6Interface

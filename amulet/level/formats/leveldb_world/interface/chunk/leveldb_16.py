from __future__ import annotations

from .leveldb_15 import (
    LevelDB15Interface,
)


class LevelDB16Interface(LevelDB15Interface):
    chunk_version = 16


export = LevelDB16Interface

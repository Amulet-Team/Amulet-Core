from __future__ import annotations

from .leveldb_19 import (
    LevelDB19Interface,
)


class LevelDB20Interface(LevelDB19Interface):
    chunk_version = 20


export = LevelDB20Interface

from __future__ import annotations

from .leveldb_16 import (
    LevelDB16Interface,
)


class LevelDB17Interface(LevelDB16Interface):
    chunk_version = 17


export = LevelDB17Interface

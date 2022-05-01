from __future__ import annotations

from .leveldb_12 import (
    LevelDB12Interface,
)


class LevelDB13Interface(LevelDB12Interface):
    chunk_version = 13


export = LevelDB13Interface

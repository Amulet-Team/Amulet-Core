from __future__ import annotations

from .leveldb_11 import (
    LevelDB11Interface,
)


class LevelDB12Interface(LevelDB11Interface):
    chunk_version = 12


export = LevelDB12Interface

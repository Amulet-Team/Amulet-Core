from __future__ import annotations

from .leveldb_0 import (
    LevelDB0Interface,
)


class LevelDB1Interface(LevelDB0Interface):
    chunk_version = 1


export = LevelDB1Interface

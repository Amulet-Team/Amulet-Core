from __future__ import annotations

from .leveldb_39 import (
    LevelDB39Interface as ParentInterface,
)


class LevelDB40Interface(ParentInterface):
    chunk_version = 40


export = LevelDB40Interface

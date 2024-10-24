from __future__ import annotations

from .leveldb_40 import (
    LevelDB40Interface as ParentInterface,
)


class LevelDB41Interface(ParentInterface):
    chunk_version = 41

    def __init__(self):
        super().__init__()


export = LevelDB41Interface

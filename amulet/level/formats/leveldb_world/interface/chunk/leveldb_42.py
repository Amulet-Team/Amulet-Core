from __future__ import annotations

from .leveldb_41 import (
    LevelDB41Interface as ParentInterface,
)


class LevelDB42Interface(ParentInterface):
    chunk_version = 42

    def __init__(self):
        super().__init__()


export = LevelDB42Interface

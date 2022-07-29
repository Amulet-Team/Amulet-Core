from __future__ import annotations

from .leveldb_39 import (
    LevelDB39Interface as ParentInterface,
)


class LevelDB40Interface(ParentInterface):
    chunk_version = 40

    def __init__(self):
        super().__init__()
        self._set_feature("entities", "actor")


export = LevelDB40Interface

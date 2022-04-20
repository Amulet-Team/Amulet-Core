from __future__ import annotations

from .leveldb_39 import (
    LevelDB39Interface as ParentInterface,
)


class LevelDB40Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 40)


export = LevelDB40Interface

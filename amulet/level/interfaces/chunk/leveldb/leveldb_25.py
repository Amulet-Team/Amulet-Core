from __future__ import annotations

from .leveldb_24 import (
    LevelDB24Interface as ParentInterface,
)


class LevelDB25Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 25)


export = LevelDB25Interface

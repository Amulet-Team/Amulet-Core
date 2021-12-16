from .leveldb_22 import (
    LevelDB22Interface as ParentInterface,
)


class LevelDB23Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 23)


export = LevelDB23Interface

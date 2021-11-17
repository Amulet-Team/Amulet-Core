from .leveldb_23 import (
    LevelDB23Interface as ParentInterface,
)


class LevelDB24Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 24)


export = LevelDB24Interface

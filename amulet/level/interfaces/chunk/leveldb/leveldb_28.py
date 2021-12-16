from .leveldb_27 import (
    LevelDB27Interface as ParentInterface,
)


class LevelDB28Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 28)


export = LevelDB28Interface

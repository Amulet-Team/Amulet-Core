from .leveldb_30 import (
    LevelDB30Interface as ParentInterface,
)


class LevelDB31Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 31)


export = LevelDB31Interface

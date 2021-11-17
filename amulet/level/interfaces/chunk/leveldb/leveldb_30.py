from .leveldb_29 import (
    LevelDB29Interface as ParentInterface,
)


class LevelDB30Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 30)


export = LevelDB30Interface

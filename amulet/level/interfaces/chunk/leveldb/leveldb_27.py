from .leveldb_26 import (
    LevelDB26Interface as ParentInterface,
)


class LevelDB27Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 27)


export = LevelDB27Interface

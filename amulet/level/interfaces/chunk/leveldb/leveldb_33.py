from .leveldb_32 import (
    LevelDB32Interface as ParentInterface,
)


class LevelDB33Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 33)


export = LevelDB33Interface

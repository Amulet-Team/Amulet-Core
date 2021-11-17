from .leveldb_31 import (
    LevelDB31Interface as ParentInterface,
)


class LevelDB32Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 32)


export = LevelDB32Interface

from .leveldb_25 import (
    LevelDB25Interface as ParentInterface,
)


class LevelDB26Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 26)


export = LevelDB26Interface

from .leveldb_37 import (
    LevelDB37Interface as ParentInterface,
)


class LevelDB38Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 38)


export = LevelDB38Interface

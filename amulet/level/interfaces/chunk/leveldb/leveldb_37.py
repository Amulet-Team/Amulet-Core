from .leveldb_36 import (
    LevelDB36Interface as ParentInterface,
)


class LevelDB37Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 37)


export = LevelDB37Interface

from .leveldb_35 import (
    LevelDB35Interface as ParentInterface,
)


class LevelDB36Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 36)


export = LevelDB36Interface

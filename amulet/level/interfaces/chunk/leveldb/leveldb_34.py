from .leveldb_33 import (
    LevelDB33Interface as ParentInterface,
)


class LevelDB34Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 34)


export = LevelDB34Interface

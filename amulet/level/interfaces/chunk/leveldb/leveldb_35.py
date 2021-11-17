from .leveldb_34 import (
    LevelDB34Interface as ParentInterface,
)


class LevelDB35Interface(ParentInterface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 35)


export = LevelDB35Interface

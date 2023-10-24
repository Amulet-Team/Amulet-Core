from .leveldb_34 import (
    LevelDB34Interface as ParentInterface,
)


class LevelDB35Interface(ParentInterface):
    chunk_version = 35


export = LevelDB35Interface

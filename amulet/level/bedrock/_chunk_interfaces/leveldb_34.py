from .leveldb_33 import (
    LevelDB33Interface as ParentInterface,
)


class LevelDB34Interface(ParentInterface):
    chunk_version = 34


export = LevelDB34Interface

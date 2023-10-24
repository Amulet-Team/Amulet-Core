from .leveldb_29 import (
    LevelDB29Interface as ParentInterface,
)


class LevelDB30Interface(ParentInterface):
    chunk_version = 30


export = LevelDB30Interface

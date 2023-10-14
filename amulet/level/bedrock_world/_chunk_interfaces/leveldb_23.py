from .leveldb_22 import (
    LevelDB22Interface as ParentInterface,
)


class LevelDB23Interface(ParentInterface):
    chunk_version = 23


export = LevelDB23Interface

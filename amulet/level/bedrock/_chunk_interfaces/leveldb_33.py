from .leveldb_32 import (
    LevelDB32Interface as ParentInterface,
)


class LevelDB33Interface(ParentInterface):
    chunk_version = 33


export = LevelDB33Interface

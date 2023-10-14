from .leveldb_37 import (
    LevelDB37Interface as ParentInterface,
)


class LevelDB38Interface(ParentInterface):
    chunk_version = 38


export = LevelDB38Interface

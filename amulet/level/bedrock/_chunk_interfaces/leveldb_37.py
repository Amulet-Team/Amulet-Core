from .leveldb_36 import (
    LevelDB36Interface as ParentInterface,
)


class LevelDB37Interface(ParentInterface):
    chunk_version = 37


export = LevelDB37Interface

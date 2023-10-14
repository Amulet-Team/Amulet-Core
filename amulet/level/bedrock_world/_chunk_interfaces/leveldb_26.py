from .leveldb_25 import (
    LevelDB25Interface as ParentInterface,
)


class LevelDB26Interface(ParentInterface):
    chunk_version = 26


export = LevelDB26Interface

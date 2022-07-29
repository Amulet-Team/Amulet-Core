from .leveldb_23 import (
    LevelDB23Interface as ParentInterface,
)


class LevelDB24Interface(ParentInterface):
    chunk_version = 24


export = LevelDB24Interface

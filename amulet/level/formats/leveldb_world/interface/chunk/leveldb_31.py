from .leveldb_30 import (
    LevelDB30Interface as ParentInterface,
)


class LevelDB31Interface(ParentInterface):
    chunk_version = 31


export = LevelDB31Interface

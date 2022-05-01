from .leveldb_26 import (
    LevelDB26Interface as ParentInterface,
)


class LevelDB27Interface(ParentInterface):
    chunk_version = 27


export = LevelDB27Interface

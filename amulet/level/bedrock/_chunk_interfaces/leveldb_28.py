from .leveldb_27 import (
    LevelDB27Interface as ParentInterface,
)


class LevelDB28Interface(ParentInterface):
    chunk_version = 28


export = LevelDB28Interface

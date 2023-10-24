from .leveldb_31 import (
    LevelDB31Interface as ParentInterface,
)


class LevelDB32Interface(ParentInterface):
    chunk_version = 32


export = LevelDB32Interface

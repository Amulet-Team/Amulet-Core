from .leveldb_35 import (
    LevelDB35Interface as ParentInterface,
)


class LevelDB36Interface(ParentInterface):
    chunk_version = 36


export = LevelDB36Interface

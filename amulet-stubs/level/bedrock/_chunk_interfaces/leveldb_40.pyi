from .leveldb_39 import LevelDB39Interface as ParentInterface

class LevelDB40Interface(ParentInterface):
    chunk_version: int
    def __init__(self) -> None: ...
export = LevelDB40Interface

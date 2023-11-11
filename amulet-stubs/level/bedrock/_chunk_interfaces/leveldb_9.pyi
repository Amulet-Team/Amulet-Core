from .leveldb_8 import LevelDB8Interface as LevelDB8Interface
from amulet.api.wrapper import EntityIDType as EntityIDType

class LevelDB9Interface(LevelDB8Interface):
    chunk_version: int
    def __init__(self) -> None: ...
export = LevelDB9Interface

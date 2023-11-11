from .base_leveldb_interface import BaseLevelDBInterface as BaseLevelDBInterface
from amulet.api.wrapper import EntityCoordType as EntityCoordType, EntityIDType as EntityIDType

class LevelDB0Interface(BaseLevelDBInterface):
    chunk_version: int
    def __init__(self) -> None: ...
export = LevelDB0Interface

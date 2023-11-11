from .leveldb_24 import LevelDB24Interface as ParentInterface

class LevelDB25Interface(ParentInterface):
    chunk_version: int
    @staticmethod
    def _get_sub_chunk_storage_byte(cy: int, min_y: int) -> bytes: ...
export = LevelDB25Interface

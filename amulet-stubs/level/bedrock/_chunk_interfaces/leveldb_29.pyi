from .leveldb_28 import LevelDB28Interface as ParentInterface
from amulet.api.chunk.blocks import Blocks as Blocks
from amulet.api.data_types import AnyNDArray as AnyNDArray, VersionNumberTuple as VersionNumberTuple

class LevelDB29Interface(ParentInterface):
    chunk_version: int
    def __init__(self) -> None: ...
    @staticmethod
    def _get_sub_chunk_storage_byte(cy: int, min_y: int) -> bytes: ...
export = LevelDB29Interface

from .leveldb_2 import LevelDB2Interface as LevelDB2Interface
from amulet.api.chunk.blocks import Blocks as Blocks
from amulet.api.data_types import AnyNDArray as AnyNDArray, VersionIdentifierTuple as VersionIdentifierTuple
from amulet.utils.world_utils import to_nibble_array as to_nibble_array
from typing import Dict, Optional, Tuple

class LevelDB3Interface(LevelDB2Interface):
    chunk_version: int
    def __init__(self) -> None: ...
    def _encode_subchunks(self, blocks: Blocks, palette: AnyNDArray, bounds: Tuple[int, int], max_world_version: VersionIdentifierTuple) -> Dict[int, Optional[bytes]]: ...
export = LevelDB3Interface

from .leveldb_7 import LevelDB7Interface as LevelDB7Interface
from amulet.api.chunk.blocks import Blocks as Blocks
from amulet.api.data_types import AnyNDArray as AnyNDArray, VersionIdentifierTuple as VersionIdentifierTuple
from amulet.block import Block as Block, PropertyDataTypes as PropertyDataTypes
from amulet.utils.numpy_helpers import brute_sort_objects_no_hash as brute_sort_objects_no_hash
from numpy.typing import NDArray as NDArray
from typing import Dict, Optional, Tuple

PackedBlockT = Tuple[Tuple[Optional[int], Block], ...]

class LevelDB8Interface(LevelDB7Interface):
    chunk_version: int
    def __init__(self) -> None: ...
    def _encode_subchunks(self, blocks: Blocks, palette: AnyNDArray, bounds: Tuple[int, int], max_world_version: VersionIdentifierTuple) -> Dict[int, Optional[bytes]]: ...
export = LevelDB8Interface

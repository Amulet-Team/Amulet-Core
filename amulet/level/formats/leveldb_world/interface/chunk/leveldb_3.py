from __future__ import annotations

from typing import Tuple, Dict, Optional, TYPE_CHECKING

import numpy

from amulet.utils.world_utils import to_nibble_array
from amulet.api.data_types import (
    AnyNDArray,
    VersionIdentifierTuple,
)
from .leveldb_2 import (
    LevelDB2Interface,
)

if TYPE_CHECKING:
    from amulet.api.chunk.blocks import Blocks


class LevelDB3Interface(LevelDB2Interface):

    chunk_version = 3

    def __init__(self):
        super().__init__()
        self._set_feature("terrain", "2farray")

    def _encode_subchunks(
        self,
        blocks: "Blocks",
        palette: AnyNDArray,
        bounds: Tuple[int, int],
        max_world_version: VersionIdentifierTuple,
    ) -> Dict[int, Optional[bytes]]:
        # encode sub-chunk block format 0
        sections = {}
        palette = numpy.array([b[0][1] for b in palette])
        for cy in range(16):
            if cy in blocks:
                block_sub_array = palette[
                    numpy.transpose(blocks.get_sub_chunk(cy), (0, 2, 1)).ravel()
                ]
                if not numpy.any(block_sub_array):
                    sections[cy] = None
                    continue

                data_sub_array = block_sub_array[:, 1]
                block_sub_array = block_sub_array[:, 0]
                sections[cy] = (
                    b"\00"
                    + block_sub_array.astype("uint8").tobytes()
                    + to_nibble_array(data_sub_array).tobytes()
                )

        return sections


export = LevelDB3Interface

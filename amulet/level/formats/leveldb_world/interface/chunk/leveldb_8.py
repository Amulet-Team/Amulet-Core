from __future__ import annotations

from .leveldb_7 import (
    LevelDB7Interface,
)

from typing import Tuple, Dict, Optional, TYPE_CHECKING, List

import struct
import numpy
from numpy.typing import NDArray
from amulet_nbt import NamedTag, CompoundTag, StringTag, IntTag, ShortTag

from amulet.api.block import Block, PropertyDataTypes

from amulet.utils.numpy_helpers import brute_sort_objects_no_hash
from amulet.api.data_types import (
    AnyNDArray,
    VersionIdentifierTuple,
)

if TYPE_CHECKING:
    from amulet.api.chunk.blocks import Blocks


PackedBlockT = Tuple[Tuple[Optional[int], Block], ...]


class LevelDB8Interface(LevelDB7Interface):
    chunk_version = 8

    def __init__(self):
        super().__init__()
        self._set_feature("terrain", "2fnpalette")

    def _encode_subchunks(
        self,
        blocks: "Blocks",
        palette: AnyNDArray,
        bounds: Tuple[int, int],
        max_world_version: VersionIdentifierTuple,
    ) -> Dict[int, Optional[bytes]]:
        # Encode sub-chunk block format 8
        # TODO: untangle this mess. The lack of typing in numpy is just making this harder.
        palette_list: List[PackedBlockT] = list(palette)
        min_y = bounds[0] // 16
        max_y = bounds[1] // 16
        if palette_list:
            if palette_list[0][0][0] is None:
                air = NamedTag(
                    CompoundTag(
                        {
                            "name": StringTag("minecraft:air"),
                            "val": ShortTag(0),
                        }
                    )
                )
            else:
                air = NamedTag(
                    CompoundTag(
                        {
                            "name": StringTag("minecraft:air"),
                            "states": CompoundTag({}),
                            "version": IntTag(17_629_184),  # 1, 13, 0, 0
                        }
                    )
                )

            packed_palette: List[Tuple[NamedTag, ...]] = []
            for index, block in enumerate(palette_list):
                full_block: List[NamedTag] = []
                for sub_block_version, sub_block in block:
                    properties = sub_block.properties
                    if sub_block_version is None:
                        block_data = properties.get("block_data", IntTag(0))
                        if isinstance(block_data, IntTag):
                            block_data = block_data.py_int
                            # if block_data >= 16:
                            #     block_data = 0
                        else:
                            block_data = 0
                        sub_block_ = NamedTag(
                            CompoundTag(
                                {
                                    "name": StringTag(sub_block.namespaced_name),
                                    "val": ShortTag(block_data),
                                }
                            )
                        )
                    else:
                        sub_block_ = NamedTag(
                            CompoundTag(
                                {
                                    "name": StringTag(sub_block.namespaced_name),
                                    "states": CompoundTag(
                                        {
                                            key: val
                                            for key, val in properties.items()
                                            if isinstance(val, PropertyDataTypes)
                                        }
                                    ),
                                    "version": IntTag(sub_block_version),
                                }
                            )
                        )

                    full_block.append(sub_block_)
                packed_palette.append(tuple(full_block))

            chunk = {}
            palette_depth = numpy.array([len(block) for block in packed_palette])
            for cy in range(min_y, max_y):
                if cy in blocks:
                    palette_index, sub_chunk = numpy.unique(
                        blocks.get_sub_chunk(cy), return_inverse=True
                    )
                    sub_chunk_palette: List[Tuple[NamedTag, ...]] = [
                        packed_palette[i] for i in palette_index
                    ]
                    sub_chunk_depth = palette_depth[palette_index].max()

                    if (
                        sub_chunk_depth == 1
                        and len(sub_chunk_palette) == 1
                        and sub_chunk_palette[0][0].compound.get_string("name").py_str
                        == "minecraft:air"
                    ):
                        chunk[cy] = None
                    else:
                        # pad block_palette with air in the extra layers
                        sub_chunk_palette_full: NDArray[NamedTag] = numpy.empty(
                            (len(sub_chunk_palette), sub_chunk_depth), dtype=object
                        )
                        sub_chunk_palette_full.fill(air)

                        for index, block_tuple in enumerate(sub_chunk_palette):
                            for sub_index, block in enumerate(block_tuple):
                                sub_chunk_palette_full[index, sub_index] = block
                        # should now be a 2D array with an NamedTag in each element

                        if max_world_version[1] >= (
                            1,
                            17,
                            30,
                        ):  # Why do I need to check against game version and not chunk version
                            sub_chunk_bytes = [
                                b"\x09",
                                bytes([sub_chunk_depth]),
                                struct.pack("b", cy),
                            ]
                        else:
                            sub_chunk_bytes = [b"\x08", bytes([sub_chunk_depth])]
                        for sub_chunk_layer_index in range(sub_chunk_depth):
                            # TODO: sort out a way to do this quicker without brute forcing it.
                            (
                                sub_chunk_layer_palette,
                                sub_chunk_remap,
                            ) = brute_sort_objects_no_hash(
                                sub_chunk_palette_full[:, sub_chunk_layer_index]
                            )
                            sub_chunk_layer = sub_chunk_remap[sub_chunk.ravel()]

                            # sub_chunk_layer, sub_chunk_layer_palette = sub_chunk, sub_chunk_palette_full[:, sub_chunk_layer_index]
                            sub_chunk_bytes.append(
                                self._save_palette_subchunk(
                                    sub_chunk_layer.reshape(16, 16, 16),
                                    list(sub_chunk_layer_palette.ravel()),
                                )
                            )

                        chunk[cy] = b"".join(sub_chunk_bytes)
                else:
                    chunk[cy] = None
        else:
            chunk = {i: None for i in range(min_y, max_y)}

        return chunk


export = LevelDB8Interface

from __future__ import annotations

from .leveldb_7 import (
    LevelDB7Interface,
)

from typing import Tuple, Dict, Optional, TYPE_CHECKING

import struct
import numpy
import amulet_nbt

from amulet.api.block import Block, PropertyDataTypes

from amulet.utils.numpy_helpers import brute_sort_objects_no_hash
from amulet.utils.world_utils import fast_unique
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberTuple,
)

if TYPE_CHECKING:
    from amulet.api.chunk.blocks import Blocks


class LevelDB8Interface(LevelDB7Interface):
    def __init__(self):
        super().__init__()

        self._set_feature("chunk_version", 8)
        self._set_feature("terrain", "2fnpalette")

    def _encode_subchunks(
        self,
        blocks: "Blocks",
        palette: AnyNDArray,
        bounds: Tuple[int, int],
        max_world_version: VersionNumberTuple,
    ) -> Dict[int, Optional[bytes]]:
        # Encode sub-chunk block format 8
        palette_depth = numpy.array([len(block) for block in palette])
        min_y = bounds[0] // 16
        max_y = bounds[1] // 16
        if palette.size:
            if palette[0][0][0] is None:
                air = amulet_nbt.NBTFile(
                    amulet_nbt.TAG_Compound(
                        {
                            "name": amulet_nbt.TAG_String("minecraft:air"),
                            "val": amulet_nbt.TAG_Short(0),
                        }
                    )
                )
            else:
                air = amulet_nbt.NBTFile(
                    amulet_nbt.TAG_Compound(
                        {
                            "name": amulet_nbt.TAG_String("minecraft:air"),
                            "states": amulet_nbt.TAG_Compound({}),
                            "version": amulet_nbt.TAG_Int(17_629_184),  # 1, 13, 0, 0
                        }
                    )
                )

            for index, block in enumerate(palette):
                block: Tuple[Tuple[Optional[int], Block], ...]
                full_block = []
                for sub_block_version, sub_block in block:
                    properties = sub_block.properties
                    if sub_block_version is None:
                        block_data = properties.get("block_data", amulet_nbt.TAG_Int(0))
                        if isinstance(block_data, amulet_nbt.TAG_Int):
                            block_data = block_data.value
                            # if block_data >= 16:
                            #     block_data = 0
                        else:
                            block_data = 0
                        sub_block_ = amulet_nbt.NBTFile(
                            amulet_nbt.TAG_Compound(
                                {
                                    "name": amulet_nbt.TAG_String(
                                        sub_block.namespaced_name
                                    ),
                                    "val": amulet_nbt.TAG_Short(block_data),
                                }
                            )
                        )
                    else:
                        sub_block_ = amulet_nbt.NBTFile(
                            amulet_nbt.TAG_Compound(
                                {
                                    "name": amulet_nbt.TAG_String(
                                        sub_block.namespaced_name
                                    ),
                                    "states": amulet_nbt.TAG_Compound(
                                        {
                                            key: val
                                            for key, val in properties.items()
                                            if isinstance(val, PropertyDataTypes)
                                        }
                                    ),
                                    "version": amulet_nbt.TAG_Int(sub_block_version),
                                }
                            )
                        )

                    full_block.append(sub_block_)
                palette[index] = tuple(full_block)

            chunk = {}
            for cy in range(min_y, max_y):
                if cy in blocks:
                    palette_index, sub_chunk = fast_unique(blocks.get_sub_chunk(cy))
                    sub_chunk_palette = palette[palette_index]
                    sub_chunk_depth = palette_depth[palette_index].max()

                    if (
                        sub_chunk_depth == 1
                        and len(sub_chunk_palette) == 1
                        and sub_chunk_palette[0][0]["name"].value == "minecraft:air"
                    ):
                        chunk[cy] = None
                    else:
                        # pad block_palette with air in the extra layers
                        sub_chunk_palette_full = numpy.empty(
                            (sub_chunk_palette.size, sub_chunk_depth), dtype=object
                        )
                        sub_chunk_palette_full.fill(air)

                        for index, block_tuple in enumerate(sub_chunk_palette):
                            for sub_index, block in enumerate(block_tuple):
                                sub_chunk_palette_full[index, sub_index] = block
                        # should now be a 2D array with an amulet_nbt.NBTFile in each element

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

from __future__ import annotations

import logging
from typing import Dict, Set, Tuple, Iterable, Optional, TYPE_CHECKING

import numpy
from amulet_nbt import (
    CompoundTag,
    ListTag,
    StringTag,
    LongArrayTag,
    LongTag,
    ShortTag,
)

from amulet.api.data_types import AnyNDArray, BlockCoordinates
from amulet.block import Block
from amulet.api.chunk import StatusFormats
from .base_anvil_interface import ChunkDataType, ChunkPathType
from .anvil_na import AnvilNAInterface as ParentInterface
from amulet.utils.world_utils import (
    decode_long_array,
    encode_long_array,
)

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

log = logging.getLogger(__name__)


class Anvil1444Interface(ParentInterface):
    """
    Moved TerrainPopulated and LightPopulated to Status
    Made blocks paletted
    Added more tick tags
    Added structures tag
    """

    TerrainPopulated = None
    LightPopulated = None

    ToBeTicked: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("ToBeTicked", ListTag)],
        ListTag,
    )

    LiquidTicks: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("LiquidTicks", ListTag)],
        ListTag,
    )
    LiquidsToBeTicked: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("LiquidsToBeTicked", ListTag)],
        ListTag,
    )

    PostProcessing: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("PostProcessing", ListTag)],
        ListTag,
    )

    Structures: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("Structures", CompoundTag)],
        CompoundTag,
    )

    LongArrayDense = True

    def __init__(self):
        super().__init__()

        self._register_decoder(self._decode_fluid_ticks)
        self._register_decoder(self._decode_post_processing)
        self._register_decoder(self._decode_structures)

        self._register_encoder(self._encode_fluid_ticks)
        self._register_encoder(self._encode_post_processing)
        self._register_encoder(self._encode_structures)

    @staticmethod
    def minor_is_valid(key: int):
        return 1444 <= key < 1466

    @staticmethod
    def _decode_block_palette(palette: ListTag) -> list:
        blockstates = []
        for entry in palette:
            namespace, base_name = entry.get_string("Name").py_str.split(":", 1)
            properties = entry.get_compound("Properties", CompoundTag({})).py_dict
            block = Block(
                namespace=namespace, base_name=base_name, properties=properties
            )
            blockstates.append(block)
        return blockstates

    @staticmethod
    def _decode_to_be_ticked(ticks: ListTag, floor_cy: int) -> Set[BlockCoordinates]:
        section_ticks: ListTag
        pos: ShortTag
        ticks_out = set()
        for cy, section_ticks in enumerate(ticks):
            block_cy = (floor_cy + cy) << 4
            for pos in section_ticks:
                pos_int = pos.py_int
                # TODO: check if these are correct. The order may be wrong.
                x = pos_int & 0xF
                y = (pos_int >> 4) & 0xF
                z = (pos_int >> 8) & 0xF
                ticks_out.add((x, block_cy + y, z))
        return ticks_out

    def _decode_block_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        super()._decode_block_ticks(chunk, data, floor_cy, height_cy)
        chunk.misc["to_be_ticked"] = self._decode_to_be_ticked(
            self.get_layer_obj(data, self.ToBeTicked, pop_last=True), floor_cy
        )

    def _decode_fluid_ticks(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, __):
        chunk.misc.setdefault("fluid_ticks", {}).update(
            self._decode_ticks(
                self.get_layer_obj(data, self.LiquidTicks, pop_last=True)
            )
        )
        chunk.misc["liquids_to_be_ticked"] = self._decode_to_be_ticked(
            self.get_layer_obj(data, self.LiquidsToBeTicked, pop_last=True), floor_cy
        )

    def _decode_post_processing(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["post_processing"] = self._decode_to_be_ticked(
            self.get_layer_obj(data, self.PostProcessing, pop_last=True), floor_cy
        )

    def _decode_structures(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["structures"] = self.get_layer_obj(
            data, self.Structures, pop_last=True
        )

    @staticmethod
    def _encode_to_be_ticked(
        ticks: Set[BlockCoordinates], floor_cy: int, height_cy: int
    ) -> ListTag:
        ceil_cy = floor_cy + height_cy
        ticks_out = ListTag([ListTag([], 2) for _ in range(floor_cy, ceil_cy)])
        if isinstance(ticks, set):
            for k in ticks:
                try:
                    (x, y, z) = k
                    cy = y >> 4
                    if floor_cy <= cy < ceil_cy:
                        x = x & 15
                        y = y & 15
                        z = z & 15
                        ticks_out[cy].append(ShortTag((z << 8) + (y << 4) + x))
                except Exception:
                    log.error(f"Could not serialise tick data {k}")
        return ticks_out

    def _encode_block_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        super()._encode_block_ticks(chunk, data, floor_cy, height_cy)
        self.set_layer_obj(
            data,
            self.ToBeTicked,
            self._encode_to_be_ticked(
                chunk.misc.get("to_be_ticked"), floor_cy, height_cy
            ),
        )

    def _encode_fluid_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data,
            self.LiquidTicks,
            self._encode_ticks(chunk.misc.get("fluid_ticks", {})),
        )
        self.set_layer_obj(
            data,
            self.LiquidsToBeTicked,
            self._encode_to_be_ticked(
                chunk.misc.get("liquids_to_be_ticked"), floor_cy, height_cy
            ),
        )

    def _encode_post_processing(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data,
            self.PostProcessing,
            self._encode_to_be_ticked(
                chunk.misc.get("post_processing"), floor_cy, height_cy
            ),
        )

    def _encode_structures(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data,
            self.Structures,
            chunk.misc.get(
                "structures",
                CompoundTag(
                    {
                        "References": CompoundTag(),
                        "Starts": CompoundTag(),
                    }
                ),
            ),
        )


export = Anvil1444Interface

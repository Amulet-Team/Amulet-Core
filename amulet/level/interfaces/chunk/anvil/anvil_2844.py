from __future__ import annotations
from typing import Tuple, Dict, Optional, Iterable
import numpy

from amulet_nbt import (
    CompoundTag,
    ListTag,
    IntTag,
    LongTag,
    LongArrayTag,
    StringTag,
)

from amulet.api.chunk import Chunk
from amulet.palette import BiomePalette
from amulet.api.data_types import AnyNDArray, BiomeType
from amulet.utils.world_utils import (
    decode_long_array,
    encode_long_array,
)

from .base_anvil_interface import (
    ChunkDataType,
    ChunkPathType,
)
from .anvil_1444 import (
    Anvil1444Interface as ParentInterface,
)


class Anvil2844Interface(ParentInterface):
    """
    Note that some of these changes happened in earlier snapshots
    Chunk restructuring
    Contents of Level tag moved into root
    Some tags renamed from PascalCase to snake_case
        2844
        Level.Entities -> entities.
        Level.TileEntities -> block_entities.
        Level.TileTicks and Level.ToBeTicked have moved to block_ticks.
        Level.LiquidTicks and Level.LiquidsToBeTicked have moved to fluid_ticks.
        Level.Sections -> sections.
        Level.Structures -> structures.
        Level.Structures.Starts -> structures.starts.
        Level.Sections[].block_states -> sections[].block_states.
        Level.Sections[].biomes -> sections[].biomes
        Added yPos the minimum section y position in the chunk.
        Added below_zero_retrogen containing data to support below zero generation.
        Added blending_data containing data to support blending new world generation with existing chunks.
        2836
        Level.Sections[].BlockStates & Level.Sections[].Palette -> Level.Sections[].block_states.
        Level.Biomes -> Level.Sections[].biomes.
        Level.CarvingMasks[] is now long[] instead of byte[].
    """

    OldLevel: ChunkPathType = ("region", [("Level", CompoundTag)], CompoundTag)
    Level: ChunkPathType = ("region", [], CompoundTag)
    Sections: ChunkPathType = ("region", [("sections", ListTag)], ListTag)

    BlockTicks: ChunkPathType = ("region", [("block_ticks", ListTag)], ListTag)
    ToBeTicked = None
    LiquidTicks: ChunkPathType = ("region", [("fluid_ticks", ListTag)], ListTag)
    LiquidsToBeTicked = None
    Structures: ChunkPathType = ("region", [("structures", CompoundTag)], CompoundTag)

    # Changed attributes not listed on the wiki
    PostProcessing: ChunkPathType = ("region", [("PostProcessing", ListTag)], ListTag)

    def __init__(self):
        super().__init__()
        self._register_post_encoder(self._post_encode_remove_old_level)

    @staticmethod
    def minor_is_valid(key: int):
        return 2844 <= key <= 3337

    def _decode_block_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc.setdefault("block_ticks", {}).update(
            self._decode_ticks(self.get_layer_obj(data, self.BlockTicks, pop_last=True))
        )

    def _decode_fluid_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc.setdefault("fluid_ticks", {}).update(
            self._decode_ticks(
                self.get_layer_obj(data, self.LiquidTicks, pop_last=True)
            )
        )

    def _encode_block_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data, self.BlockTicks, self._encode_ticks(chunk.misc.get("block_ticks", {}))
        )

    def _encode_fluid_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data,
            self.LiquidTicks,
            self._encode_ticks(chunk.misc.get("fluid_ticks", {})),
        )

    def _post_encode_remove_old_level(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.get_layer_obj(data, self.OldLevel, pop_last=True)


export = Anvil2844Interface

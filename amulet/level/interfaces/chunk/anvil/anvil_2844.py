from __future__ import annotations
from typing import Tuple, Dict
import numpy


import amulet_nbt
from amulet_nbt import (
    TAG_Byte,
    TAG_Int,
    TAG_Long,
    TAG_Byte_Array,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Int_Array,
    TAG_Long_Array,
    NBTFile,
)

import amulet
from amulet import log
from amulet.api.chunk import Chunk, StatusFormats
from amulet.api.data_types import AnyNDArray
from amulet.utils.world_utils import decode_long_array, encode_long_array
from .feature_enum import BiomeState

from .anvil_2709 import (
    Anvil2709Interface as ParentInterface,
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

    BlockEntities = "block_entities"
    Entities = "entities"
    Sections = "sections"
    Structures = "structures"

    @staticmethod
    def minor_is_valid(key: int):
        return 2844 <= key < 2900

    def _decode_chunk(
        self, chunk: Chunk, root: TAG_Compound, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        self._decode_root(chunk, root)
        self._decode_level(chunk, root, bounds)
        sections = self._extract_sections(chunk, root)
        self._decode_sections(chunk, sections)
        palette = self._decode_blocks(chunk, sections)
        return chunk, palette

    def _decode_level(self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]):
        self._decode_last_update(chunk, level)
        self._decode_status(chunk, level)
        self._decode_inhabited_time(chunk, level)
        self._decode_height(chunk, level, bounds)
        self._decode_entities(chunk, level)
        self._decode_block_entities(chunk, level)
        self._decode_block_ticks(chunk, level)
        self._decode_block_ticks(chunk, level)
        self._decode_fluid_ticks(chunk, level)
        self._decode_post_processing(chunk, level)
        self._decode_structures(chunk, level)

    def _decode_sections(self, chunk: Chunk, sections: Dict[int, TAG_Compound]):
        super()._decode_sections(chunk, sections)
        self._decode_biome_sections(chunk, sections)

    def _decode_biome_sections(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ):
        raise NotImplementedError

    def _decode_block_ticks(self, chunk: Chunk, compound: TAG_Compound):
        raise NotImplementedError

    def _decode_fluid_ticks(self, chunk: Chunk, compound: TAG_Compound):
        raise NotImplementedError


export = Anvil2844Interface

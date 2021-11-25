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

from .anvil_2529 import (
    Anvil2529Interface as ParentInterface,
)


class Anvil2844Interface(ParentInterface):
    BlockStatesKey = "block_states"

    @staticmethod
    def minor_is_valid(key: int):
        return 2844 <= key < 2900

    def decode(
        self, cx: int, cz: int, nbt_file: NBTFile, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        # new code
        chunk, compound = self._init_decode(cx, cz, nbt_file)
        self._remove_data_version(compound)

        self._decode_last_update(chunk, compound)
        self._decode_status(chunk, compound)
        self._decode_inhabited_time(chunk, compound)
        self._decode_height(chunk, compound)
        sections = self._extract_sections(chunk, compound, "sections")
        palette = self._decode_blocks(chunk, sections)
        self._decode_biome_sections(chunk, sections)
        self._decode_block_light(chunk, sections)
        self._decode_sky_light(chunk, sections)
        self._decode_entities(chunk, compound)
        self._decode_block_entities(chunk, compound, "block_entities")
        # TODO look into the new format for this
        # self._decode_tile_ticks(chunk, compound, "block_ticks")

        # self._decode_liquid_ticks(chunk, compound, "fluid_ticks")

        self._decode_post_processing(chunk, compound)
        self._decode_structures(chunk, compound, "structures")
        return chunk, palette

    def _decode_biome_sections(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ):
        raise NotImplementedError


export = Anvil2844Interface

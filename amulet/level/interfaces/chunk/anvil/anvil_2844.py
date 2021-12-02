from __future__ import annotations
from typing import Tuple, Dict, Optional
import numpy

from amulet_nbt import (
    TAG_Compound,
    TAG_List,
)

from amulet.api.chunk import Chunk
from amulet.api.registry import BiomeManager
from amulet.api.data_types import AnyNDArray, BiomeType
from amulet.utils.world_utils import (
    decode_long_array,
    encode_long_array,
)

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
        floor_cy = root.pop("yPos").value
        self._decode_level(chunk, root, bounds, floor_cy)
        sections = self._extract_sections(chunk, root)
        self._decode_sections(chunk, sections)
        palette = self._decode_blocks(chunk, sections)
        return chunk, palette

    def _decode_level(
        self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int], floor_cy: int
    ):
        self._decode_coords(chunk, level)
        self._decode_last_update(chunk, level)
        self._decode_status(chunk, level)
        self._decode_inhabited_time(chunk, level)
        self._decode_height(chunk, level, bounds)
        self._decode_entities(chunk, level)
        self._decode_block_entities(chunk, level)
        self._decode_block_ticks(chunk, level, floor_cy)
        self._decode_fluid_ticks(chunk, level, floor_cy)
        self._decode_post_processing(chunk, level, floor_cy)
        self._decode_structures(chunk, level)

    @staticmethod
    def _decode_location(chunk: Chunk, level: TAG_Compound):
        assert chunk.coordinates == (level.pop("xPos"), level.pop("zPos"))
        level.pop("yPos")

    def _decode_sections(self, chunk: Chunk, sections: Dict[int, TAG_Compound]):
        super()._decode_sections(chunk, sections)
        self._decode_biome_sections(chunk, sections)

    def _decode_block_section(
        self, section: TAG_Compound
    ) -> Optional[Tuple[numpy.ndarray, list]]:
        block_states = self.get_obj(section, "block_states", TAG_Compound)
        if (
            isinstance(block_states, TAG_Compound) and "palette" in block_states
        ):  # 1.14 makes block_palette/blocks optional.
            section_palette = self._decode_block_palette(block_states.pop("palette"))
            data = block_states.pop("data", None)
            if data is None:
                arr = numpy.zeros((16, 16, 16), numpy.uint32)
            else:
                decoded = decode_long_array(
                    data.value,
                    16 ** 3,
                    max(4, (len(section_palette) - 1).bit_length()),
                    dense=self.LongArrayDense,
                ).astype(numpy.uint32)
                arr = numpy.transpose(decoded.reshape((16, 16, 16)), (2, 0, 1))
            return arr, section_palette
        else:
            return None

    @staticmethod
    def _decode_biome_palette(palette: TAG_List) -> list[BiomeType]:
        return [entry.value for entry in palette]

    def _decode_biome_section(
        self, section: TAG_Compound
    ) -> Optional[Tuple[numpy.ndarray, list]]:
        biomes = self.get_obj(section, "biomes", TAG_Compound)
        if isinstance(biomes, TAG_Compound) and "palette" in biomes:
            section_palette = self._decode_biome_palette(biomes.pop("palette"))
            data = biomes.pop("data", None)
            if data is None:
                # TODO: in the new biome system just leave this as the number
                arr = numpy.zeros((4, 4, 4), numpy.uint32)
            else:
                arr = numpy.transpose(
                    decode_long_array(
                        data.value,
                        4 ** 3,
                        (len(section_palette) - 1).bit_length(),
                        dense=self.LongArrayDense,
                    )
                    .astype(numpy.uint32)
                    .reshape((4, 4, 4)),
                    (2, 0, 1),
                )
            return arr, section_palette
        else:
            return None

    def _decode_biome_sections(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ):
        biomes: Dict[int, numpy.ndarray] = {}
        palette = BiomeManager()

        for cy, section in chunk_sections.items():
            data = self._decode_biome_section(section)
            if data is not None:
                arr, section_palette = data
                lut = numpy.array(
                    [palette.get_add_biome(biome) for biome in section_palette]
                )
                biomes[cy] = lut[arr].astype(numpy.uint32)

        chunk.biomes = biomes
        chunk.biome_palette = palette

    def _decode_block_ticks(self, chunk: Chunk, compound: TAG_Compound, floor_cy: int):
        chunk.misc.setdefault("block_ticks", {}).update(
            self._decode_ticks(self.get_obj(compound, "block_ticks", TAG_List))
        )

    def _decode_fluid_ticks(self, chunk: Chunk, compound: TAG_Compound, floor_cy: int):
        chunk.misc.setdefault("fluid_ticks", {}).update(
            self._decode_ticks(self.get_obj(compound, "fluid_ticks", TAG_List))
        )

    def _encode_block_ticks(
        self, chunk: Chunk, compound: TAG_Compound, bounds: Tuple[int, int]
    ):
        compound["block_ticks"] = self._encode_ticks(chunk.misc.get("block_ticks", {}))

    def _encode_fluid_ticks(
        self, chunk: Chunk, compound: TAG_Compound, bounds: Tuple[int, int]
    ):
        compound["fluid_ticks"] = self._encode_ticks(chunk.misc.get("fluid_ticks", {}))


export = Anvil2844Interface

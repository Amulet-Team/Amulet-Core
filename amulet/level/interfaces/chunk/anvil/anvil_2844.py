from __future__ import annotations
from typing import Tuple, Dict, Optional
import numpy

from amulet_nbt import (
    TAG_Compound,
    TAG_List,
    TAG_Byte,
    TAG_Int,
    TAG_Long_Array,
    TAG_String,
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
        return 2844 <= key < 2976

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
                    16**3,
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
                        4**3,
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

    def _encode_chunk(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, int],
        bounds: Tuple[int, int],
    ) -> TAG_Compound:
        root = self._init_encode(chunk)
        self._encode_root(root, max_world_version)
        self._encode_level(chunk, root, bounds)
        sections = self._init_sections(chunk)
        self._encode_sections(chunk, sections, bounds)
        self._encode_blocks(chunk, sections, palette, bounds)
        sections_list = []
        for cy, section in sections.items():
            section["Y"] = TAG_Byte(cy)
            sections_list.append(section)
        root[self.Sections] = TAG_List(sections_list)
        return root

    def _encode_level(self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]):
        self._encode_coords(chunk, level, bounds)
        self._encode_last_update(chunk, level)
        self._encode_status(chunk, level)
        self._encode_inhabited_time(chunk, level)
        self._encode_height(chunk, level, bounds)
        self._encode_entities(chunk, level)
        self._encode_block_entities(chunk, level)
        self._encode_block_ticks(chunk, level, bounds)
        self._encode_fluid_ticks(chunk, level, bounds)
        self._encode_post_processing(chunk, level, bounds)
        self._encode_structures(chunk, level)

    def _encode_coords(
        self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    ):
        super()._encode_coords(chunk, level, bounds)
        level["yPos"] = TAG_Int(bounds[0] >> 4)

    def _encode_sections(
        self, chunk: Chunk, sections: Dict[int, TAG_Compound], bounds: Tuple[int, int]
    ):
        super()._encode_sections(chunk, sections, bounds)
        self._encode_biome_sections(chunk, sections, bounds)

    def _encode_block_section(
        self,
        chunk: Chunk,
        sections: Dict[int, TAG_Compound],
        palette: AnyNDArray,
        cy: int,
    ):
        if cy in chunk.blocks:
            block_sub_array = numpy.transpose(
                chunk.blocks.get_sub_chunk(cy), (1, 2, 0)
            ).ravel()

            sub_palette_, block_sub_array = numpy.unique(
                block_sub_array, return_inverse=True
            )
            sub_palette = self._encode_block_palette(palette[sub_palette_])
            section = sections.setdefault(cy, TAG_Compound())
            block_states = section["block_states"] = TAG_Compound(
                {"palette": sub_palette}
            )
            if len(sub_palette) != 1:
                block_states["data"] = TAG_Long_Array(
                    encode_long_array(
                        block_sub_array, dense=self.LongArrayDense, min_bits_per_entry=4
                    )
                )
            return True
        return False

    @staticmethod
    def _encode_biome_palette(palette: list[BiomeType]) -> TAG_List:
        return TAG_List([TAG_String(entry) for entry in palette])

    def _encode_biome_section(
        self,
        chunk: Chunk,
        sections: Dict[int, TAG_Compound],
        cy: int,
    ) -> bool:
        chunk.biomes.convert_to_3d()
        if cy in chunk.biomes:
            biome_sub_array = numpy.transpose(
                chunk.biomes.get_section(cy), (1, 2, 0)
            ).ravel()

            sub_palette_, biome_sub_array = numpy.unique(
                biome_sub_array, return_inverse=True
            )
            sub_palette = self._encode_biome_palette(chunk.biome_palette[sub_palette_])
            section = sections.setdefault(cy, TAG_Compound())
            biomes = section["biomes"] = TAG_Compound({"palette": sub_palette})
            if len(sub_palette) != 1:
                biomes["data"] = TAG_Long_Array(
                    encode_long_array(biome_sub_array, dense=self.LongArrayDense)
                )
            return True
        return False

    def _encode_biome_sections(
        self,
        chunk: Chunk,
        sections: Dict[int, TAG_Compound],
        bounds: Tuple[int, int],
    ):
        for cy in range(bounds[0] >> 4, bounds[1] >> 4):
            self._encode_biome_section(chunk, sections, cy)

    def _encode_block_ticks(
        self, chunk: Chunk, compound: TAG_Compound, bounds: Tuple[int, int]
    ):
        compound["block_ticks"] = self._encode_ticks(chunk.misc.get("block_ticks", {}))

    def _encode_fluid_ticks(
        self, chunk: Chunk, compound: TAG_Compound, bounds: Tuple[int, int]
    ):
        compound["fluid_ticks"] = self._encode_ticks(chunk.misc.get("fluid_ticks", {}))


export = Anvil2844Interface

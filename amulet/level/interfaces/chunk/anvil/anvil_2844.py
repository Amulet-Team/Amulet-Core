from __future__ import annotations
from typing import Tuple, Dict, Optional
import numpy

from amulet_nbt import (
    CompoundTag,
    ListTag,
    ByteTag,
    IntTag,
    LongTag,
    LongArrayTag,
    StringTag,
)

from amulet.api.chunk import Chunk
from amulet.api.registry import BiomeManager
from amulet.api.data_types import AnyNDArray, BiomeType
from amulet.utils.world_utils import (
    decode_long_array,
    encode_long_array,
)

from .base_anvil_interface import (
    ChunkDataType,
    ChunkPathType,
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

    Level: ChunkPathType = ("region", [], CompoundTag)
    Sections: ChunkPathType = ("region", [("sections", ListTag)], ListTag)

    BlockEntities: ChunkPathType = ("region", [("block_entities", ListTag)], ListTag)
    Entities: ChunkPathType = ("region", [("entities", ListTag)], ListTag)
    InhabitedTime: ChunkPathType = ("region", [("InhabitedTime", LongTag)], LongTag)
    LastUpdate: ChunkPathType = ("region", [("LastUpdate", LongTag)], LongTag)
    Heightmaps: ChunkPathType = ("region", [("Heightmaps", CompoundTag)], CompoundTag)
    BlockTicks: ChunkPathType = ("region", [("block_ticks", ListTag)], ListTag)
    ToBeTicked = None
    Biomes = None

    Status: ChunkPathType = ("region", [("Status", StringTag)], StringTag("full"))

    LiquidTicks: ChunkPathType = ("region", [("fluid_ticks", ListTag)], ListTag)
    PostProcessing: ChunkPathType = ("region", [("PostProcessing", ListTag)], ListTag)

    Structures: ChunkPathType = ("region", [("structures", CompoundTag)], CompoundTag)

    yPos: ChunkPathType = ("region", [("yPos", IntTag)], IntTag)

    @staticmethod
    def minor_is_valid(key: int):
        return 2844 <= key < 3150

    def _get_floor_cy(self, data: ChunkDataType):
        return self.get_layer_obj(data, self.yPos, pop_last=True).py_int

    def _decode_block_section(
        self, section: CompoundTag
    ) -> Optional[Tuple[numpy.ndarray, list]]:
        block_states = self.get_obj(section, "block_states", CompoundTag)
        if (
            isinstance(block_states, CompoundTag) and "palette" in block_states
        ):  # 1.14 makes block_palette/blocks optional.
            section_palette = self._decode_block_palette(block_states.pop("palette"))
            data = block_states.pop("data", None)
            if data is None:
                arr = numpy.zeros((16, 16, 16), numpy.uint32)
            else:
                decoded = decode_long_array(
                    data.np_array,
                    16**3,
                    max(4, (len(section_palette) - 1).bit_length()),
                    dense=self.LongArrayDense,
                ).astype(numpy.uint32)
                arr = numpy.transpose(decoded.reshape((16, 16, 16)), (2, 0, 1))
            return arr, section_palette
        else:
            return None

    @staticmethod
    def _decode_biome_palette(palette: ListTag) -> list[BiomeType]:
        return [entry.py_data for entry in palette]

    def _decode_biome_section(
        self, section: CompoundTag
    ) -> Optional[Tuple[numpy.ndarray, list]]:
        biomes = self.get_obj(section, "biomes", CompoundTag)
        if isinstance(biomes, CompoundTag) and "palette" in biomes:
            section_palette = self._decode_biome_palette(biomes.pop("palette"))
            data = biomes.pop("data", None)
            if data is None:
                # TODO: in the new biome system just leave this as the number
                arr = numpy.zeros((4, 4, 4), numpy.uint32)
            else:
                arr = numpy.transpose(
                    decode_long_array(
                        data.np_array,
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

    def _decode_biomes(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        biomes: Dict[int, numpy.ndarray] = {}
        palette = BiomeManager()

        for cy, section in self._iter_sections(data):
            data = self._decode_biome_section(section)
            if data is not None:
                arr, section_palette = data
                lut = numpy.array(
                    [palette.get_add_biome(biome) for biome in section_palette]
                )
                biomes[cy] = lut[arr].astype(numpy.uint32)

        chunk.biomes = biomes
        chunk.biome_palette = palette

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

    def _encode_coords(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        super()._encode_coords(chunk, data, floor_cy, height_cy)
        self.set_layer_obj(data, self.yPos, IntTag(floor_cy))

    def _encode_block_section(
        self,
        chunk: Chunk,
        sections: Dict[int, CompoundTag],
        palette: AnyNDArray,
        cy: int,
    ):
        block_sub_array = numpy.transpose(
            chunk.blocks.get_sub_chunk(cy), (1, 2, 0)
        ).ravel()

        sub_palette_, block_sub_array = numpy.unique(
            block_sub_array, return_inverse=True
        )
        sub_palette = self._encode_block_palette(palette[sub_palette_])
        section = sections.setdefault(cy, CompoundTag())
        block_states = section["block_states"] = CompoundTag({"palette": sub_palette})
        if len(sub_palette) != 1:
            block_states["data"] = LongArrayTag(
                encode_long_array(
                    block_sub_array, dense=self.LongArrayDense, min_bits_per_entry=4
                )
            )

    @staticmethod
    def _encode_biome_palette(palette: list[BiomeType]) -> ListTag:
        return ListTag([StringTag(entry) for entry in palette])

    def _encode_biome_section(
        self,
        chunk: Chunk,
        sections: Dict[int, CompoundTag],
        cy: int,
    ):
        biome_sub_array = numpy.transpose(
            chunk.biomes.get_section(cy), (1, 2, 0)
        ).ravel()

        sub_palette_, biome_sub_array = numpy.unique(
            biome_sub_array, return_inverse=True
        )
        sub_palette = self._encode_biome_palette(chunk.biome_palette[sub_palette_])
        biomes = sections[cy]["biomes"] = CompoundTag({"palette": sub_palette})
        if len(sub_palette) != 1:
            biomes["data"] = LongArrayTag(
                encode_long_array(biome_sub_array, dense=self.LongArrayDense)
            )

    def _encode_biomes(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        sections = self._get_encode_sections(data, floor_cy, height_cy)
        ceil_cy = floor_cy + height_cy
        chunk.biomes.convert_to_3d()
        for cy in chunk.biomes.sections:
            if floor_cy <= cy < ceil_cy:
                self._encode_biome_section(chunk, sections, cy)

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


export = Anvil2844Interface

from __future__ import annotations

from typing import Tuple, Dict, TYPE_CHECKING

import numpy
from amulet_nbt import TAG_Compound, TAG_Byte_Array, NBTFile, TAG_Byte, TAG_List

from amulet.api.data_types import SubChunkNDArray, AnyNDArray
from amulet.utils import world_utils
from amulet.api.wrapper import EntityIDType, EntityCoordType
from .base_anvil_interface import (
    BaseAnvilInterface,
)
from .feature_enum import BiomeState, HeightState

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk
    from amulet.api.chunk.blocks import Blocks


class AnvilNAInterface(BaseAnvilInterface):
    def __init__(self):
        super().__init__()
        self._set_feature("data_version", "int")
        self._set_feature("last_update", "long")

        self._set_feature("light_populated", "byte")
        self._set_feature("terrain_populated", "byte")
        self._set_feature("inhabited_time", "long")
        self._set_feature("biomes", BiomeState.BA256)
        self._set_feature("height_state", HeightState.Fixed256)
        self._set_feature("height_map", "256IA")

        self._set_feature("blocks", "Sections|(Blocks,Data,Add)")
        self._set_feature("block_light", "Sections|2048BA")
        self._set_feature("sky_light", "Sections|2048BA")
        self._set_feature("light_optional", "false")

        self._set_feature("block_entities", "list")
        self._set_feature("block_entity_format", EntityIDType.namespace_str_id)
        self._set_feature("block_entity_coord_format", EntityCoordType.xyz_int)

        self._set_feature("entities", "list")
        self._set_feature("entity_format", EntityIDType.namespace_str_id)
        self._set_feature("entity_coord_format", EntityCoordType.Pos_list_double)

        self._set_feature("tile_ticks", "list")

    @staticmethod
    def minor_is_valid(key: int):
        return key == -1

    def decode(
        self, cx: int, cz: int, nbt_file: NBTFile, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        chunk, compound = self._init_decode(cx, cz, nbt_file)
        self._remove_data_version(compound)
        assert self.check_type(compound, "Level", TAG_Compound)
        level = compound["Level"]
        self._decode_last_update(chunk, level)
        self._decode_status(chunk, level)
        self._decode_inhabited_time(chunk, level)
        self._decode_biomes(chunk, level)
        self._decode_height(chunk, level)
        sections = self._extract_sections(chunk, level)
        palette = self._decode_blocks(chunk, sections)
        self._decode_block_light(chunk, sections)
        self._decode_sky_light(chunk, sections)
        self._decode_entities(chunk, level)
        self._decode_block_entities(chunk, level)
        self._decode_block_ticks(chunk, level)
        return chunk, palette

    def _decode_status(self, chunk: Chunk, compound: TAG_Compound):
        status = "empty"
        if self._features["terrain_populated"] == "byte" and self.get_obj(
            compound, "TerrainPopulated", TAG_Byte
        ):
            status = "decorated"
        if self._features["light_populated"] == "byte" and self.get_obj(
            compound, "LightPopulated", TAG_Byte
        ):
            status = "postprocessed"

        chunk.status = status

    def _decode_blocks(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ) -> AnyNDArray:
        blocks: Dict[int, SubChunkNDArray] = {}
        palette = []
        palette_len = 0
        for cy, section in chunk_sections.items():
            section_blocks = numpy.frombuffer(
                section.pop("Blocks").value, dtype=numpy.uint8
            )
            section_data = numpy.frombuffer(
                section.pop("Data").value, dtype=numpy.uint8
            )
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks = section_blocks.astype(numpy.uint16)

            section_data = world_utils.from_nibble_array(section_data)
            section_data = section_data.reshape((16, 16, 16))

            if "Add" in section:
                add_blocks = numpy.frombuffer(
                    section.pop("Add").value, dtype=numpy.uint8
                )
                add_blocks = world_utils.from_nibble_array(add_blocks)
                add_blocks = add_blocks.reshape((16, 16, 16))

                section_blocks |= add_blocks.astype(numpy.uint16) << 8
                # TODO: fix this

            (section_palette, blocks[cy]) = world_utils.fast_unique(
                numpy.transpose(
                    (section_blocks << 4) + section_data, (2, 0, 1)
                )  # YZX -> XYZ
            )
            blocks[cy] += palette_len
            palette_len += len(section_palette)
            palette.append(section_palette)

        if palette:
            final_palette, lut = numpy.unique(
                numpy.concatenate(palette), return_inverse=True
            )
            final_palette: numpy.ndarray = numpy.array(
                [final_palette >> 4, final_palette & 15]
            ).T
            for cy in blocks:
                blocks[cy] = lut[blocks[cy]]
        else:
            final_palette = numpy.array([], dtype=object)
        chunk.blocks = blocks
        return final_palette

    def _decode_block_ticks(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["tile_ticks"] = self.get_obj(compound, "TileTicks", TAG_List)

    def _encode_blocks(
        self,
        sections: Dict[int, TAG_Compound],
        blocks: "Blocks",
        palette: AnyNDArray,
        cy_min: int,
        cy_max: int,
    ):
        added_sections = set()
        for cy in range(cy_min, cy_max):
            if cy in blocks:
                block_sub_array = palette[
                    numpy.transpose(
                        blocks.get_sub_chunk(cy), (1, 2, 0)
                    ).ravel()  # XYZ -> YZX
                ]

                data_sub_array = block_sub_array[:, 1]
                block_sub_array = block_sub_array[:, 0]
                if not numpy.any(block_sub_array) and not numpy.any(data_sub_array):
                    continue
                added_sections.add(cy)
                section = sections.setdefault(cy, TAG_Compound())
                section["Blocks"] = TAG_Byte_Array(block_sub_array.astype("uint8"))
                section["Data"] = TAG_Byte_Array(
                    world_utils.to_nibble_array(data_sub_array)
                )
        # In 1.12.2 and before if the Blocks key does not exist but the sub-chunk TAG_Compound does
        # exist the game will error and recreate the chunk. All sub-chunks that do not contain data
        # must be deleted.
        for cy in list(sections):
            if cy not in added_sections:
                del sections[cy]


export = AnvilNAInterface

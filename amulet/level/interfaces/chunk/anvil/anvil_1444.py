from __future__ import annotations

from typing import Tuple, Dict, TYPE_CHECKING

import numpy
from amulet_nbt import (
    TAG_Compound,
    NBTFile,
    TAG_List,
    TAG_String,
    TAG_Long_Array,
    TAG_Byte_Array,
)

from amulet.api.data_types import AnyNDArray, SubChunkNDArray
from amulet.api.block import Block
from amulet.api.chunk import Blocks, StatusFormats
from amulet.api.wrapper import EntityIDType, EntityCoordType
from .base_anvil_interface import (
    BaseAnvilInterface,
)
from amulet.utils.world_utils import (
    decode_long_array,
    encode_long_array,
)
from .feature_enum import BiomeState, HeightState

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


def properties_to_string(props: dict) -> str:
    """
    Converts a dictionary of blockstate properties to a string

    :param props: The dictionary of blockstate properties
    :return: The string version of the supplied blockstate properties
    """
    result = []
    for key, value in props.items():
        result.append("{}={}".format(key, value))
    return ",".join(result)


class Anvil1444Interface(BaseAnvilInterface):
    BlockStatesKey = "BlockStates"

    def __init__(self):
        super().__init__()
        self._set_feature("data_version", "int")
        self._set_feature("last_update", "long")

        self._set_feature("status", StatusFormats.Java_13)
        self._set_feature("inhabited_time", "long")
        self._set_feature("biomes", BiomeState.BA256)
        self._set_feature("height_state", HeightState.Fixed256)
        self._set_feature("height_map", "256IA")

        self._set_feature("blocks", "Sections|(BlockStates,Palette)")
        self._set_feature("long_array_format", "compact")
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

        self._set_feature("liquid_ticks", "list")
        self._set_feature("liquids_to_be_ticked", "16list|list")
        self._set_feature("to_be_ticked", "16list|list")
        self._set_feature("post_processing", "16list|list")
        self._set_feature("structures", "compound")

    @staticmethod
    def minor_is_valid(key: int):
        return 1444 <= key < 1466

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
        self._decode_fluid_ticks(chunk, level)
        self._decode_post_processing(chunk, level)
        self._decode_structures(chunk, level)
        return chunk, palette

    def _decode_status(self, chunk: Chunk, compound: TAG_Compound):
        chunk.status = self.get_obj(
            compound, "Status", TAG_String, TAG_String("full")
        ).value

    def _decode_biomes(self, chunk: Chunk, compound: TAG_Compound):
        biomes = compound.pop("Biomes")
        if isinstance(biomes, TAG_Byte_Array) and biomes.value.size == 256:
            chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))

    def _decode_blocks(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ) -> AnyNDArray:
        blocks: Dict[int, numpy.ndarray] = {}
        palette = [Block(namespace="minecraft", base_name="air")]

        for cy, section in chunk_sections.items():
            if "Palette" not in section:  # 1.14 makes block_palette/blocks optional.
                continue
            section_palette = self._decode_palette(section.pop("Palette"))
            if self._features["long_array_format"] in ("compact", "1.16"):
                decoded = decode_long_array(
                    section.pop("BlockStates").value,
                    4096,
                    max(4, (len(section_palette) - 1).bit_length()),
                    dense=self._features["long_array_format"] == "compact",
                ).astype(numpy.uint32)
            else:
                raise Exception(
                    "long_array_format", self._features["long_array_format"]
                )
            blocks[cy] = numpy.transpose(
                decoded.reshape((16, 16, 16)) + len(palette), (2, 0, 1)
            )
            palette += section_palette

        np_palette, inverse = numpy.unique(palette, return_inverse=True)
        np_palette: numpy.ndarray
        inverse: numpy.ndarray
        inverse = inverse.astype(numpy.uint32)
        for cy in blocks:
            blocks[cy] = inverse[blocks[cy]]
        chunk.blocks = blocks
        return np_palette

    def _decode_block_ticks(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["tile_ticks"] = self.get_obj(compound, "TileTicks", TAG_List)
        chunk.misc["to_be_ticked"] = self.get_obj(compound, "ToBeTicked", TAG_List)

    def _decode_fluid_ticks(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["liquid_ticks"] = self.get_obj(compound, "LiquidTicks", TAG_List)
        chunk.misc["liquids_to_be_ticked"] = self.get_obj(
            compound, "LiquidsToBeTicked", TAG_List
        )

    def _encode_blocks(
        self,
        sections: Dict[int, TAG_Compound],
        blocks: Blocks,
        palette: AnyNDArray,
        cy_min: int,
        cy_max: int,
    ):
        for cy in range(cy_min, cy_max):
            if cy in blocks:
                block_sub_array = numpy.transpose(
                    blocks.get_sub_chunk(cy), (1, 2, 0)
                ).ravel()

                sub_palette_, block_sub_array = numpy.unique(
                    block_sub_array, return_inverse=True
                )
                sub_palette = self._encode_palette(palette[sub_palette_])
                if (
                    len(sub_palette) == 1
                    and sub_palette[0]["Name"].value == "minecraft:air"
                ):
                    continue

                section = sections.setdefault(cy, TAG_Compound())
                if self._features["long_array_format"] == "compact":
                    section["BlockStates"] = TAG_Long_Array(
                        encode_long_array(block_sub_array, min_bits_per_entry=4)
                    )
                elif self._features["long_array_format"] == "1.16":
                    section["BlockStates"] = TAG_Long_Array(
                        encode_long_array(
                            block_sub_array, dense=False, min_bits_per_entry=4
                        )
                    )
                section["Palette"] = sub_palette

    @staticmethod
    def _decode_palette(palette: TAG_List) -> list:
        blockstates = []
        for entry in palette:
            namespace, base_name = entry["Name"].value.split(":", 1)
            properties = entry.get("Properties", TAG_Compound({})).value
            block = Block(
                namespace=namespace, base_name=base_name, properties=properties
            )
            blockstates.append(block)
        return blockstates

    @staticmethod
    def _encode_palette(blockstates: list) -> TAG_List:
        palette = TAG_List()
        for block in blockstates:
            entry = TAG_Compound()
            entry["Name"] = TAG_String(f"{block.namespace}:{block.base_name}")
            entry["Properties"] = TAG_Compound(block.properties)
            palette.append(entry)
        return palette


export = Anvil1444Interface

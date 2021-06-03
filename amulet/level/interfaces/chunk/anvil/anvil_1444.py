from __future__ import annotations

from typing import Tuple, Dict

import numpy
import amulet_nbt

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

    def _decode_blocks(
        self, chunk_sections: Dict[int, amulet_nbt.TAG_Compound]
    ) -> Tuple[Dict[int, SubChunkNDArray], AnyNDArray]:
        blocks: Dict[int, numpy.ndarray] = {}
        palette = [Block(namespace="minecraft", base_name="air")]

        for cy, section in chunk_sections.items():
            if "Palette" not in section:  # 1.14 makes block_palette/blocks optional.
                continue
            if self._features["long_array_format"] == "compact":
                decoded = decode_long_array(section.pop("BlockStates").value, 4096)
            elif self._features["long_array_format"] == "1.16":
                decoded = decode_long_array(
                    section.pop("BlockStates").value, 4096, dense=False
                )
            else:
                raise Exception("long_array_format", self._features["long_array_format"])
            blocks[cy] = numpy.transpose(
                decoded.reshape((16, 16, 16)) + len(palette), (2, 0, 1)
            )

            palette += self._decode_palette(section.pop("Palette"))

        np_palette, inverse = numpy.unique(palette, return_inverse=True)
        np_palette: numpy.ndarray
        inverse: numpy.ndarray
        for cy in blocks:
            blocks[cy] = inverse[blocks[cy]].astype(
                numpy.uint32
            )  # TODO: find a way to make the new blocks format change dtype
        return blocks, np_palette

    def _encode_blocks(
        self,
        sections: Dict[int, amulet_nbt.TAG_Compound],
        blocks: Blocks,
        palette: AnyNDArray,
    ):
        for cy in range(16):
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

                section = sections.setdefault(cy, amulet_nbt.TAG_Compound())
                if self._features["long_array_format"] == "compact":
                    section["BlockStates"] = amulet_nbt.TAG_Long_Array(
                        encode_long_array(block_sub_array)
                    )
                elif self._features["long_array_format"] == "1.16":
                    section["BlockStates"] = amulet_nbt.TAG_Long_Array(
                        encode_long_array(block_sub_array, dense=False)
                    )
                section["Palette"] = sub_palette

    @staticmethod
    def _decode_palette(palette: amulet_nbt.TAG_List) -> list:
        blockstates = []
        for entry in palette:
            namespace, base_name = entry["Name"].value.split(":", 1)
            properties = entry.get("Properties", amulet_nbt.TAG_Compound({})).value
            block = Block(
                namespace=namespace, base_name=base_name, properties=properties
            )
            blockstates.append(block)
        return blockstates

    @staticmethod
    def _encode_palette(blockstates: list) -> amulet_nbt.TAG_List:
        palette = amulet_nbt.TAG_List()
        for block in blockstates:
            entry = amulet_nbt.TAG_Compound()
            entry["Name"] = amulet_nbt.TAG_String(
                f"{block.namespace}:{block.base_name}"
            )
            entry["Properties"] = amulet_nbt.TAG_Compound(block.properties)
            palette.append(entry)
        return palette


export = Anvil1444Interface

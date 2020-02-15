from __future__ import annotations

from typing import Tuple

import numpy
import amulet_nbt as nbt

from amulet.api.block import Block
from amulet.world_interface.chunk.interfaces.anvil.base_anvil_interface import (
    BaseAnvilInterface,
)
from amulet.utils.world_utils import (
    get_smallest_dtype,
    decode_long_array,
    encode_long_array,
)


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
        BaseAnvilInterface.__init__(self)
        self.features["data_version"] = "int"
        self.features["last_update"] = "long"

        self.features["status"] = "j13"
        self.features["inhabited_time"] = "long"
        self.features["biomes"] = "256BA"
        self.features["height_map"] = "C5|36LA"

        self.features["blocks"] = "Sections|(BlockStates,Palette)"
        self.features["block_light"] = "Sections|2048BA"
        self.features["sky_light"] = "Sections|2048BA"

        self.features["block_entities"] = "list"
        self.features["block_entity_format"] = "namespace-str-id"
        self.features["block_entity_coord_format"] = "xyz-int"

        self.features["entities"] = "list"
        self.features["entity_format"] = "namespace-str-id"
        self.features["entity_coord_format"] = "Pos-list-double"

        self.features["tile_ticks"] = "list"

        self.features["liquid_ticks"] = "list"
        self.features["liquids_to_be_ticked"] = "16list|list"
        self.features["to_be_ticked"] = "16list|list"
        self.features["post_processing"] = "16list|list"
        self.features["structures"] = "compound"

    @staticmethod
    def minor_is_valid(key: int):
        return 1444 <= key < 1466

    def _decode_blocks(self, chunk_sections) -> Tuple[numpy.ndarray, numpy.ndarray]:
        if chunk_sections is None:
            raise NotImplementedError(
                "We don't support reading chunks that never been edited in Minecraft before"
            )

        blocks = numpy.zeros((256, 16, 16), dtype=int)
        palette = [Block(namespace="minecraft", base_name="air")]

        for section in chunk_sections:
            if "Palette" not in section:  # 1.14 makes palette/blocks optional.
                continue
            height = section["Y"].value << 4

            blocks[height : height + 16, :, :] = decode_long_array(
                section["BlockStates"].value, 4096
            ).reshape((16, 16, 16)) + len(palette)

            palette += self._decode_palette(section["Palette"])

        blocks = numpy.swapaxes(blocks.swapaxes(0, 1), 0, 2)
        palette, inverse = numpy.unique(palette, return_inverse=True)
        blocks = inverse[blocks]

        return blocks.astype(f"uint{get_smallest_dtype(blocks)}"), palette

    def _encode_blocks(
        self, blocks: numpy.ndarray, palette: numpy.ndarray
    ) -> nbt.TAG_List:
        sections = nbt.TAG_List()
        blocks = numpy.swapaxes(blocks.swapaxes(0, 2), 0, 1)
        for y in range(16):  # perhaps find a way to do this dynamically
            block_sub_array = blocks[y * 16 : y * 16 + 16, :, :].ravel()

            sub_palette_, block_sub_array = numpy.unique(
                block_sub_array, return_inverse=True
            )
            sub_palette = self._encode_palette(palette[sub_palette_])
            if (
                len(sub_palette) == 1
                and sub_palette[0]["Name"].value == "minecraft:air"
            ):
                continue

            section = nbt.TAG_Compound()
            section["Y"] = nbt.TAG_Byte(y)
            section["BlockStates"] = nbt.TAG_Long_Array(
                encode_long_array(block_sub_array)
            )
            section["Palette"] = sub_palette
            sections.append(section)

        return sections

    @staticmethod
    def _decode_palette(palette: nbt.TAG_List) -> list:
        blockstates = []
        for entry in palette:
            namespace, base_name = entry["Name"].value.split(":", 1)
            properties = {
                prop: str(val.value)
                for prop, val in entry.get("Properties", nbt.TAG_Compound({})).items()
            }
            block = Block(
                namespace=namespace, base_name=base_name, properties=properties
            )
            blockstates.append(block)
        return blockstates

    @staticmethod
    def _encode_palette(blockstates: list) -> nbt.TAG_List:
        palette = nbt.TAG_List()
        for block in blockstates:
            entry = nbt.TAG_Compound()
            entry["Name"] = nbt.TAG_String(f"{block.namespace}:{block.base_name}")
            properties = entry["Properties"] = nbt.TAG_Compound()
            for prop, val in block.properties.items():
                if isinstance(val, str):
                    properties[prop] = nbt.TAG_String(val)
            palette.append(entry)
        return palette


INTERFACE_CLASS = Anvil1444Interface

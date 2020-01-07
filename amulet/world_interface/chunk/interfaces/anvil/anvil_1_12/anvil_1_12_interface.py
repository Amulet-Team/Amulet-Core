from __future__ import annotations

from typing import List, Tuple

import numpy
import amulet_nbt as nbt

from amulet.utils import world_utils
from amulet.world_interface.chunk.interfaces.anvil.base_anvil_interface import (
    BaseAnvilInterface,
)


class Anvil112Interface(BaseAnvilInterface):
    def __init__(self):
        BaseAnvilInterface.__init__(self)
        self.features["data_version"] = "int"
        self.features["last_update"] = "long"

        self.features["light_populated"] = "byte"
        self.features["terrain_populated"] = "byte"
        self.features["inhabited_time"] = "long"
        self.features["biomes"] = "256BA"
        self.features["height_map"] = "256IA"

        self.features["blocks"] = "Sections|(Blocks,Data,Add)"
        self.features["block_light"] = "Sections|2048BA"
        self.features["sky_light"] = "Sections|2048BA"

        self.features["block_entities"] = "list"
        self.features["block_entity_format"] = "namespace-str-id"
        self.features["block_entity_coord_format"] = "xyz-int"

        self.features["entities"] = "list"
        self.features["entity_format"] = "namespace-str-id"
        self.features["entity_coord_format"] = "Pos-list-double"

        self.features["tile_ticks"] = "list"

    @staticmethod
    def minor_is_valid(key: int):
        return 1022 <= key < 1444

    def _decode_blocks(
        self, chunk_sections: nbt.TAG_List
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        if chunk_sections is None:
            raise NotImplementedError(
                "We don't support reading chunks that never been edited in Minecraft before"
            )

        blocks = numpy.zeros((256, 16, 16), dtype=int)
        block_data = numpy.zeros((256, 16, 16), dtype=numpy.uint8)
        for section in chunk_sections:
            lower = section["Y"].value << 4
            upper = (section["Y"].value + 1) << 4

            section_blocks = numpy.frombuffer(
                section["Blocks"].value, dtype=numpy.uint8
            )
            del section["Blocks"]
            section_data = numpy.frombuffer(section["Data"].value, dtype=numpy.uint8)
            del section["Data"]
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks.astype(numpy.uint16, copy=False)

            section_data = section_data.reshape(
                (16, 16, 8)
            )  # The Byte array is actually just Nibbles, so the size is off

            section_data = world_utils.from_nibble_array(section_data)

            if "Add" in section:
                add_blocks = numpy.frombuffer(section["Add"].value, dtype=numpy.uint8)
                del section["Add"]
                add_blocks = add_blocks.reshape((16, 16, 8))
                add_blocks = world_utils.from_nibble_array(add_blocks)

                section_blocks |= add_blocks.astype(numpy.uint16) << 8

            blocks[lower:upper, :, :] = section_blocks
            block_data[lower:upper, :, :] = section_data

        blocks = numpy.swapaxes(blocks.swapaxes(0, 1), 0, 2)
        block_data = numpy.swapaxes(block_data.swapaxes(0, 1), 0, 2)

        blocks = (blocks << 4) + block_data
        palette, blocks = world_utils.fast_unique(blocks)
        palette = numpy.array([[elm >> 4, elm & 15] for elm in palette])
        return blocks, palette

    def _encode_blocks(
        self, blocks: numpy.ndarray, palette: numpy.ndarray
    ) -> nbt.TAG_List:
        blocks = palette[blocks]
        sections = nbt.TAG_List()
        blocks = numpy.swapaxes(blocks.swapaxes(0, 2), 0, 1)
        block_array, data_array = blocks[:, :, :, 0], blocks[:, :, :, 1]
        for y in range(16):  # perhaps find a way to do this dynamically
            block_sub_array = block_array[y * 16 : y * 16 + 16, :, :].ravel()
            data_sub_array = data_array[y * 16 : y * 16 + 16, :, :].ravel()
            if not numpy.any(block_sub_array) and not numpy.any(data_sub_array):
                continue
            section = nbt.TAG_Compound()
            section["Y"] = nbt.TAG_Byte(y)
            section["Blocks"] = nbt.TAG_Byte_Array(block_sub_array.astype("uint8"))
            section["Data"] = nbt.TAG_Byte_Array(
                ((data_sub_array[::2] << 4) + data_sub_array[1::2]).astype("uint8")
            )
            sections.append(section)

        return sections


INTERFACE_CLASS = Anvil112Interface

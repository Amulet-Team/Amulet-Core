from __future__ import annotations

from typing import Tuple, Dict, TYPE_CHECKING

import numpy
import amulet_nbt as nbt

from amulet.api.data_types import SubChunkNDArray, AnyNDArray
from amulet.utils import world_utils
from amulet.world_interface.chunk.interfaces.anvil.base_anvil_interface import (
    BaseAnvilInterface,
)

if TYPE_CHECKING:
    from amulet.api.chunk.blocks import Blocks


class AnvilNAInterface(BaseAnvilInterface):
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
        return key == -1

    def _decode_blocks(
        self, chunk_sections: nbt.TAG_List
    ) -> Tuple[Dict[int, SubChunkNDArray], AnyNDArray]:
        blocks: Dict[int, SubChunkNDArray] = {}
        palette = []
        palette_len = 0
        for section in chunk_sections:
            cy: int = section["Y"].value

            section_blocks = numpy.frombuffer(
                section["Blocks"].value, dtype=numpy.uint8
            )
            del section["Blocks"]
            section_data = numpy.frombuffer(section["Data"].value, dtype=numpy.uint8)
            del section["Data"]
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks = section_blocks.astype(numpy.uint16)

            section_data = world_utils.from_nibble_array(section_data)
            section_data = section_data.reshape((16, 16, 16))

            if "Add" in section:
                add_blocks = numpy.frombuffer(section["Add"].value, dtype=numpy.uint8)
                del section["Add"]
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
            final_palette = numpy.array([], dtype=numpy.object)
        return blocks, final_palette

    def _encode_blocks(self, blocks: "Blocks", palette: AnyNDArray) -> nbt.TAG_List:
        sections = nbt.TAG_List()
        for cy in range(16):  # perhaps find a way to do this dynamically
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
                section = nbt.TAG_Compound()
                section["Y"] = nbt.TAG_Byte(cy)
                section["Blocks"] = nbt.TAG_Byte_Array(block_sub_array.astype("uint8"))
                section["Data"] = nbt.TAG_Byte_Array(
                    world_utils.to_nibble_array(data_sub_array)
                )
                sections.append(section)

        return sections


INTERFACE_CLASS = AnvilNAInterface

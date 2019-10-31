from __future__ import annotations

from typing import List, Tuple

import numpy
import amulet_nbt as nbt

from amulet.utils import world_utils
from amulet.world_interface.chunk.interfaces.base_anvil_interface import BaseAnvilInterface


class AnvilInterface(BaseAnvilInterface):
    def __init__(self):
        BaseAnvilInterface.__init__(self)
        self.args['data_version'] = 'int'
        self.args['last_update'] = 'long'

        self.args['light_populated'] = 'byte'
        self.args['terrain_populated'] = 'byte'
        self.args['inhabited_time'] = 'long'
        self.args['biomes'] = '256BA'
        self.args['height_map'] = '256IA'

        self.args['blocks'] = 'Sections|(Blocks,Data,Add)'
        self.args['block_light'] = 'Sections|2048BA'
        self.args['sky_light'] = 'Sections|2048BA'

        self.args['entities'] = 'list'
        self.args['tile_entities'] = 'list'
        self.args['tile_ticks'] = 'list'

    @staticmethod
    def is_valid(key):
        if key[0] != "anvil":
            return False
        if key[1] > 1343:
            return False
        return True

    def _decode_entities(self, entities: list) -> List[nbt.NBTFile]:
        return []
        # entity_list = []
        # for entity in entities:
        #     entity = nbt_template.create_entry_from_nbt(entity)
        #     entity = self._entity_handlers[entity["id"].value].load_entity(entity)
        #     entity_list.append(entity)
        #
        # return entity_list

    def _encode_entities(self, entities: list) -> nbt.TAG_List:
        return nbt.TAG_List([])

    def _decode_blocks(self, chunk_sections: nbt.TAG_List) -> Tuple[numpy.ndarray, numpy.ndarray]:
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
            del section['Blocks']
            section_data = numpy.frombuffer(section["Data"].value, dtype=numpy.uint8)
            del section['Data']
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks.astype(numpy.uint16, copy=False)

            section_data = section_data.reshape(
                (16, 16, 8)
            )  # The Byte array is actually just Nibbles, so the size is off

            section_data = world_utils.from_nibble_array(section_data)

            if "Add" in section:
                add_blocks = numpy.frombuffer(section["Add"].value, dtype=numpy.uint8)
                del section['Add']
                add_blocks = add_blocks.reshape((16, 16, 8))
                add_blocks = world_utils.from_nibble_array(add_blocks)

                section_blocks |= add_blocks.astype(numpy.uint16) << 8

            blocks[lower:upper, :, :] = section_blocks
            block_data[lower:upper, :, :] = section_data

        blocks = numpy.swapaxes(blocks.swapaxes(0, 1), 0, 2)
        block_data = numpy.swapaxes(block_data.swapaxes(0, 1), 0, 2)

        blocks = numpy.array((blocks, block_data)).T
        palette, blocks = numpy.unique(
            blocks.reshape(16 * 256 * 16, 2), return_inverse=True, axis=0
        )
        blocks = blocks.reshape(16, 256, 16, order="F")
        return blocks, palette

    def _encode_blocks(self, blocks: numpy.ndarray, palette: numpy.ndarray) -> nbt.TAG_List:
        blocks = palette[blocks]
        sections = nbt.TAG_List()
        block_array, data_array = blocks[:, :, :, 0], blocks[:, :, :, 1]
        for y in range(16): # perhaps find a way to do this dynamically
            block_sub_array = block_array[:, y * 16: y * 16 + 16, :].ravel()
            data_sub_array = data_array[:, y * 16: y * 16 + 16, :].ravel()
            # TODO: check if the sub-chunk is empty and skip
            section = nbt.TAG_Compound()
            section['Y'] = nbt.TAG_Byte(y)
            section['Blocks'] = nbt.TAG_Byte_Array(block_sub_array.astype('uint8'))
            section['Data'] = nbt.TAG_Byte_Array(((data_sub_array[::2] << 4) + data_sub_array[1::2]).astype('uint8'))
            sections.append(section)

        return sections

    def _get_translator_info(self, data: nbt.NBTFile) -> Tuple[Tuple[str, int], int]:
        return ("anvil", data["DataVersion"].value), data["DataVersion"].value


INTERFACE_CLASS = AnvilInterface

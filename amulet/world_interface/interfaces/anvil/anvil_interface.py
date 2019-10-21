from __future__ import annotations

from typing import List, Tuple

import numpy
import amulet_nbt as nbt

from amulet.api.chunk import Chunk
from amulet.utils import world_utils
from amulet.world_interface.interfaces import Interface
from amulet.world_interface import translators


class AnvilInterface(Interface):
    @staticmethod
    def is_valid(key):
        if key[0] != "anvil":
            return False
        if key[1] > 1343:
            return False
        return True

    def decode(self, data: nbt.NBTFile) -> Tuple[Chunk, numpy.ndarray]:
        """

        :param data: nbt.NBTFile
        :return: Tuple[ Chunk in version format, an N*2 numpy int array of block ids and data values
        """
        cx = data["Level"]["xPos"].value
        cz = data["Level"]["zPos"].value
        blocks, palette = self._decode_blocks(data["Level"]["Sections"])
        entities = self._decode_entities(data["Level"]["Entities"])
        tile_entities = None
        return Chunk(cx, cz, blocks, entities, tile_entities, extra=data), palette

    def encode(self, chunk: Chunk, palette: numpy.ndarray) -> nbt.NBTFile:
        """

        :param chunk: Chunk in version format
        :param palette: an N*2 numpy int array of block ids and data values
        :return: nbt.NBTFile
        """
        # TODO: sort out a proper location for this data and create from scratch each time
        data = chunk._extra
        data["Level"]["Sections"] = self._encode_blocks(chunk.blocks, palette)
        # TODO: sort out the other data in sections
        # data["Level"]["Entities"] = self._encode_entities(chunk.entities)
        return data

    def _decode_entities(self, entities: list) -> List[nbt.NBTFile]:
        return []
        # entity_list = []
        # for entity in entities:
        #     entity = nbt_template.create_entry_from_nbt(entity)
        #     entity = self._entity_handlers[entity["id"].value].load_entity(entity)
        #     entity_list.append(entity)
        #
        # return entity_list

    def _encode_entities(self, entities: list) -> List[nbt.NBTFile]:
        raise NotImplementedError

    def _decode_blocks(self, chunk_sections: nbt.TAG_List) -> Tuple[numpy.ndarray, numpy.ndarray]:
        if not chunk_sections:
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
            section['Blocks'] = nbt.TAG_Byte_Array(block_sub_array)
            section['Data'] = nbt.TAG_Byte_Array((data_sub_array[::2] << 4) + data_sub_array[1::2])

        return sections

    def get_translator(self, max_world_version, data: nbt.NBTFile = None) -> translators.Translator:
        if data is None:
            return translators.get_translator(max_world_version)
        else:
            return translators.get_translator(("anvil", data["DataVersion"].value))


INTERFACE_CLASS = AnvilInterface

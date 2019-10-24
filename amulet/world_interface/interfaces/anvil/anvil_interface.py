from __future__ import annotations

from typing import List, Tuple, Union, Callable

import numpy
import amulet_nbt as nbt

from amulet.api.chunk import Chunk
from amulet.utils import world_utils
from amulet.world_interface.interfaces import Interface
from amulet.world_interface import translators
import PyMCTranslate


class AnvilInterface(Interface):
    @staticmethod
    def is_valid(key):
        if key[0] != "anvil":
            return False
        if key[1] > 1343:
            return False
        return True

    def decode_and_translate(
        self,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        data: nbt.NBTFile,
        translation_manager: PyMCTranslate.TranslationManager,
        callback: Callable,
        full_translate: bool
    ) -> Tuple[Chunk, numpy.ndarray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format and translate into the universal format.
        :param max_world_version:
        :param data: nbt.NBTFile
        :param translation_manager:
        :param callback:
        :param full_translate:
        :return: Chunk object in universal format, along with the palette for that chunk.
        """
        cx = data["Level"]["xPos"].value
        cz = data["Level"]["zPos"].value
        data_version = data['DataVersion'].value
        blocks, palette = self._decode_blocks(data["Level"]["Sections"])
        entities = self._decode_entities(data["Level"]["Entities"])
        tile_entities = None
        return self._get_translator(
            max_world_version,
            data_version
        ).to_universal(
            data_version,
            translation_manager,
            Chunk(cx, cz, blocks, entities, tile_entities, extra=data),
            palette,
            callback,
            full_translate
        )

    def translate_and_encode(
        self,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        chunk: Chunk,
        palette: numpy.ndarray,
        translation_manager: PyMCTranslate.TranslationManager,
        callback: Callable,
        full_translate: bool
    ) -> nbt.NBTFile:
        """
        Translate a universal chunk and encode it to raw data for the format to store.
        :param max_world_version:
        :param chunk: The universal chunk to translate and encode.
        :param palette: The palette the ids in the chunk correspond to.
        :param translation_manager:
        :param callback:
        :param full_translate:
        :return: nbt.NBTFile
        """
        chunk, palette = self._get_translator(
            max_world_version
        ).from_universal(
            max_world_version[1],
            translation_manager,
            chunk,
            palette,
            callback,
            full_translate
        )
        # TODO: sort out a proper location for this data and create from scratch each time
        data = chunk._extra
        data["Level"]["Sections"] = self._encode_blocks(chunk._blocks, palette)
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

    def _get_translator(self, max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]], data: int = None) -> translators.Translator:
        if data is None:
            return translators.get_translator(max_world_version)
        else:
            return translators.get_translator(("anvil", data))


INTERFACE_CLASS = AnvilInterface

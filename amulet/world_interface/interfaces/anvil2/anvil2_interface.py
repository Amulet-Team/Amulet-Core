from __future__ import annotations

from typing import List, Tuple, Union, Callable

import numpy
import amulet_nbt as nbt

from amulet.api.block import Block
from amulet.api.chunk import Chunk
from amulet.world_interface.interfaces import Interface
from amulet.utils.world_utils import get_smallest_dtype, decode_long_array, encode_long_array
from amulet.world_interface import translators
import PyMCTranslate


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


class Anvil2Interface(Interface):
    @staticmethod
    def is_valid(key):
        if key[0] != "anvil":
            return False
        if key[1] < 1444:
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

    def _decode_blocks(
        self, chunk_sections
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        if not chunk_sections:
            raise NotImplementedError(
                "We don't support reading chunks that never been edited in Minecraft before"
            )

        blocks = numpy.zeros((256, 16, 16), dtype=int)
        palette = [Block(namespace="minecraft", base_name="air")]

        for section in chunk_sections:
            if "Palette" not in section:  # 1.14 makes palette/blocks optional.
                continue
            height = section["Y"].value << 4

            blocks[height: height + 16, :, :] = decode_long_array(
                section["BlockStates"].value, 4096
            ).reshape((16, 16, 16)) + len(palette)

            palette += self._decode_palette(section["Palette"])

        blocks = numpy.swapaxes(blocks.swapaxes(0, 1), 0, 2)
        palette, inverse = numpy.unique(palette, return_inverse=True)
        blocks = inverse[blocks]

        return blocks.astype(f"uint{get_smallest_dtype(blocks)}"), palette

    def _encode_blocks(self, blocks: numpy.ndarray, palette: numpy.ndarray) -> nbt.TAG_List:
        sections = nbt.TAG_List()
        for y in range(16):  # perhaps find a way to do this dynamically
            block_sub_array = blocks[:, y * 16: y * 16 + 16, :].ravel()

            sub_palette_, block_sub_array = numpy.unique(block_sub_array, return_inverse=True)
            sub_palette = self._encode_palette(palette[sub_palette_])
            if len(sub_palette) == 1 and sub_palette[0]['Name'].value == 'minecraft:air':
                continue

            section = nbt.TAG_Compound()
            section['Y'] = nbt.TAG_Byte(y)
            section['BlockStates'] = nbt.TAG_Long_Array(encode_long_array(block_sub_array))
            section['Palette'] = sub_palette
            section['BlockLight'] = nbt.TAG_Byte_Array(numpy.zeros(2048, dtype=numpy.uint8))
            section['SkyLight'] = nbt.TAG_Byte_Array(numpy.zeros(2048, dtype=numpy.uint8))
            sections.append(section)

        return sections

    @staticmethod
    def _decode_palette(palette: nbt.TAG_List) -> list:
        blockstates = []
        for entry in palette:
            namespace, base_name = entry["Name"].value.split(":", 1)
            # TODO: handle waterlogged property
            properties = {prop: str(val.value) for prop, val in entry.get("Properties", nbt.TAG_Compound({})).items()}
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
            entry['Name'] = nbt.TAG_String(f'{block.namespace}:{block.base_name}')
            properties = entry['Properties'] = nbt.TAG_Compound()
            # TODO: handle waterlogged property
            for prop, val in block.properties.items():
                if isinstance(val, str):
                    properties[prop] = nbt.TAG_String(val)
            palette.append(entry)
        return palette

    def _decode_entities(self, entities: list) -> List[nbt.NBTFile]:
        return []
        # entity_list = []
        # for entity in entities:
        #     entity = nbt_template.create_entry_from_nbt(entity)
        #     entity = self._entity_handlers[entity["id"].value].load_entity(entity)
        #     entity_list.append(entity)
        #
        # return entity_list

    def _get_translator(self, max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]], data: int = None) -> translators.Translator:
        if data is None:
            return translators.loader.get(max_world_version)
        else:
            return translators.loader.get(("anvil", data))


INTERFACE_CLASS = Anvil2Interface

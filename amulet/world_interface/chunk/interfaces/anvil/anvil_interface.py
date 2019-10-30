from __future__ import annotations

from typing import List, Tuple

import numpy
import amulet_nbt as nbt

from amulet.api.chunk import Chunk
from amulet.utils import world_utils
from amulet.world_interface.chunk.interfaces import Interface


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
        Create an amulet.api.chunk.Chunk object from raw data given by the format.
        :param data: nbt.NBTFile
        :return: Chunk object in version-specific format, along with the palette for that chunk.
        """
        misc = {}
        cx = data["Level"]["xPos"].value
        cz = data["Level"]["zPos"].value
        blocks, palette = self._decode_blocks(data["Level"]["Sections"])
        misc['BlockLight2048BA'] = {section['Y'].value: section['BlockLight'] for section in data["Level"]["Sections"]}
        misc['SkyLight2048BA'] = {section['Y'].value: section['SkyLight'] for section in data["Level"]["Sections"]}
        misc['LightPopulatedB'] = data['Level']['LightPopulated']
        misc['HeightMap256IA'] = data['Level']['HeightMap']
        misc['TileTicksA'] = data['Level'].get('TileTicks', nbt.TAG_List())
        misc['LastUpdateL'] = data['Level']['LastUpdate']
        # misc['Biomes256'] = data['Level']['Biomes']
        misc['InhabitedTimeL'] = data['Level']['InhabitedTime']
        misc['TerrainPopulatedB'] = data['Level']['TerrainPopulated']

        entities = self._decode_entities(data["Level"]["Entities"])
        tile_entities = None
        return Chunk(cx, cz, blocks, entities, tile_entities, misc=misc, extra=data), palette

    def encode(self, chunk: Chunk, palette: numpy.ndarray, max_world_version: Tuple[str, int]) -> nbt.NBTFile:
        """
        Encode a version-specific chunk to raw data for the format to store.
        :param chunk: The version-specific chunk to translate and encode.
        :param palette: The palette the ids in the chunk correspond to.
        :return: nbt.NBTFile
        """

        misc = chunk.misc
        data = nbt.NBTFile(nbt.TAG_Compound(), '')
        data['Level'] = nbt.TAG_Compound()
        data['Level']['xPos'] = nbt.TAG_Int(chunk.cx)
        data['Level']['zPos'] = nbt.TAG_Int(chunk.cz)
        data['DataVersion'] = nbt.TAG_Int(max_world_version[1])
        data["Level"]["Sections"] = self._encode_blocks(chunk._blocks, palette)
        for section in data["Level"]["Sections"]:
            y = section['Y'].value
            block_light = misc.get('BlockLight2048BA', {})
            sky_light = misc.get('SkyLight2048BA', {})
            if y in block_light:
                section['BlockLight'] = block_light[y]
            else:
                section['BlockLight'] = nbt.TAG_Byte_Array(numpy.zeros(2048, dtype=numpy.uint8))
            if y in sky_light:
                section['SkyLight'] = sky_light[y]
            else:
                section['SkyLight'] = nbt.TAG_Byte_Array(numpy.zeros(2048, dtype=numpy.uint8))
        data['Level']['LightPopulated'] = misc.get('LightPopulatedB', nbt.TAG_Byte(0))
        data['Level']['HeightMap'] = misc.get('HeightMap256IA', nbt.TAG_Int_Array(numpy.zeros(256, dtype='>u4')))
        ticks = misc.get('TileTicksA', nbt.TAG_List())
        if len(ticks) > 0:
            data['Level']['TileTicks'] = ticks
        data['Level']['LastUpdate'] = misc.get('LastUpdateL', nbt.TAG_Long(0))
        # data['Level']['Biomes'] = misc.get('Biomes256', nbt.TAG_Byte_Array(numpy.zeros(256, dtype='uint8')))
        data['Level']['Biomes'] = chunk.extra['Level']['Biomes']
        data['Level']['InhabitedTime'] = misc.get('InhabitedTimeL', nbt.TAG_Long(0))
        data['Level']['TerrainPopulated'] = misc.get('TerrainPopulatedB', nbt.TAG_Byte(0))
        data["Level"]["Entities"] = self._encode_entities(chunk.entities)
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

from __future__ import annotations

from typing import List, Tuple

import numpy
import amulet_nbt as nbt

from amulet.api.chunk import Chunk
from amulet.world_interface.chunk.interfaces import Interface


class BaseAnvilInterface(Interface):
    def __init__(self):
        arg_options = {
            'data_version': ['int'],        # int
            'last_update': ['long'],        # int
            'light_populated': ['byte'],    # int
            'terrain_populated': ['byte'],  # int
            'V': ['byte'],                  # int
            'inhabited_time': ['long'],     # int
            'biomes': ['256BA', '256IA', '1024IA'],  # Biomes
            'height_map': ['256IA', 'C6|36LA'],
            'carving_masks': ['C|?BA'],
            'blocks': ['Sections|(Blocks,Data,Add)', 'Sections|(BlockStates,Palette)'],
            'block_light': ['Sections|2048BA'],
            'sky_light': ['Sections|2048BA'],

            'entities': ['list'],
            'tile_entities': ['list'],
            'tile_ticks': ['list', 'list(optional)'],




        }
        self.args = {
            key: None for key in arg_options.keys()
        }

    def decode(self, data: nbt.NBTFile) -> Tuple[Chunk, numpy.ndarray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format.
        :param data: nbt.NBTFile
        :return: Chunk object in version-specific format, along with the palette for that chunk.
        """
        misc = {}
        cx = data["Level"]["xPos"].value
        cz = data["Level"]["zPos"].value
        chunk = Chunk(cx, cz)

        if self.args['last_update'] == 'long':
            misc['last_update'] = data['Level']['LastUpdate'].value

        if self.args['light_populated'] == 'byte':
            misc['light_populated'] = data['Level']['LightPopulated'].value

        if self.args['terrain_populated'] == 'byte':
            misc['terrain_populated'] = data['Level']['TerrainPopulated'].value

        if self.args['V'] == 'byte':
            misc['V'] = data['Level']['V'].value

        if self.args['inhabited_time'] == 'long':
            misc['inhabited_time'] = data['Level']['InhabitedTime'].value

        if self.args['biomes'] is not None:
            chunk.biomes = data['Level']['Biomes'].value

        if self.args['height_map'] == '256IA':
            misc['height_map256IA'] = data['Level']['HeightMap']
        elif self.args['height_map'] == 'C6|36LA':
            misc['height_mapC6|36LA'] = data['Level']['Heightmaps']

        if self.args['blocks'] in ['Sections|(Blocks,Data,Add)', 'Sections|(BlockStates,Palette)']:
            chunk.blocks, palette = self._decode_blocks(data["Level"]["Sections"])
        else:
            raise Exception(f'Unsupported block format {self.args["blocks"]}')

        if self.args['block_light'] == 'Sections|2048BA':
            misc['block_light'] = {section['Y'].value: section['BlockLight'] for section in data["Level"]["Sections"]}

        if self.args['sky_light'] == 'Sections|2048BA':
            misc['sky_light'] = {section['Y'].value: section['SkyLight'] for section in data["Level"]["Sections"]}

        if self.args['entities'] == 'list':
            chunk.entities = self._decode_entities(data["Level"]["Entities"])

        if self.args['tile_entities'] == 'list':
            chunk.tile_entities = None

        if self.args['tile_ticks'] == 'list':
            misc['tile_ticks'] = data['Level'].get('TileTicks', nbt.TAG_List())

        chunk.misc = misc
        chunk.extra = data

        return chunk, palette

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
        if self.args['data_version'] == 'int':
            data['DataVersion'] = nbt.TAG_Int(max_world_version[1])

        if self.args['last_update'] == 'long':
            data['Level']['LastUpdate'] = nbt.TAG_Long(misc.get('last_update', 0))

        if self.args['light_populated'] == 'byte':
            data['Level']['LightPopulated'] = nbt.TAG_Byte(misc.get('light_populated', 0))

        if self.args['terrain_populated'] == 'byte':
            data['Level']['TerrainPopulated'] = nbt.TAG_Byte(misc.get('terrain_populated', 0))

        if self.args['V'] == 'byte':
            data['Level']['V'] = nbt.TAG_Byte(misc.get('V', 1))

        if self.args['inhabited_time'] == 'long':
            data['Level']['InhabitedTime'] = nbt.TAG_Long(misc.get('inhabited_time', 0))

        if self.args['biomes'] == '256BA':
            data['Level']['Biomes'] = nbt.TAG_Byte_Array(chunk.biomes.convert_to_format(256).astype(dtype=numpy.uint8))
        elif self.args['biomes'] == '256IA':
            data['Level']['Biomes'] = nbt.TAG_Int_Array(chunk.biomes.convert_to_format(256).astype(dtype=numpy.uint32))
        elif self.args['biomes'] == '1024IA':
            data['Level']['Biomes'] = nbt.TAG_Int_Array(chunk.biomes.convert_to_format(1024).astype(dtype=numpy.uint32))

        if self.args['height_map'] == '256IA':
            data['Level']['HeightMap'] = nbt.TAG_Int_Array(misc.get('height_map256IA', numpy.zeros(256, dtype=numpy.uint32)))
        elif self.args['height_map'] == 'C6|36LA':
            heightmaps = misc.get('height_mapC6|36LA', nbt.TAG_Compound())
            for heightmap in (
                'MOTION_BLOCKING',
                'MOTION_BLOCKING_NO_LEAVES',
                'OCEAN_FLOOR',
                'OCEAN_FLOOR_WG',
                'WORLD_SURFACE',
                'WORLD_SURFACE_WG'
            ):
                if heightmap not in heightmaps:
                    heightmaps[heightmap] = nbt.TAG_Long_Array(numpy.zeros(36, dtype='>i8'))
            data['Level']['Heightmaps'] = heightmaps

        if self.args['blocks'] in ['Sections|(Blocks,Data,Add)', 'Sections|(BlockStates,Palette)']:
            data["Level"]["Sections"] = self._encode_blocks(chunk.blocks, palette)
        else:
            raise Exception(f'Unsupported block format {self.args["blocks"]}')

        if self.args['block_light'] in ['Sections|2048BA'] or self.args['sky_light'] in ['Sections|2048BA']:
            for section in data["Level"]["Sections"]:
                y = section['Y'].value
                if self.args['block_light'] == 'Sections|2048BA':
                    block_light = misc.get('block_light', {})
                    if y in block_light:
                        section['BlockLight'] = block_light[y]
                    else:
                        section['BlockLight'] = nbt.TAG_Byte_Array(numpy.full(2048, 255, dtype=numpy.uint8))
                if self.args['sky_light'] == 'Sections|2048BA':
                    sky_light = misc.get('sky_light', {})
                    if y in sky_light:
                        section['SkyLight'] = sky_light[y]
                    else:
                        section['SkyLight'] = nbt.TAG_Byte_Array(numpy.full(2048, 255, dtype=numpy.uint8))

        if self.args['entities'] == 'list':
            data["Level"]["Entities"] = self._encode_entities(chunk.entities)

        if self.args['tile_ticks'] in ['list', 'list(optional)']:
            ticks = misc.get('tile_ticks', nbt.TAG_List())
            if self.args['tile_ticks'] == 'list(optional)':
                if len(ticks) > 0:
                    data['Level']['TileTicks'] = ticks
            elif self.args['tile_ticks'] == 'list':
                data['Level']['TileTicks'] = ticks

        return data

    def _decode_entities(self, entities: list) -> List[nbt.NBTFile]:
        raise NotImplementedError

    def _encode_entities(self, entities: list) -> nbt.TAG_List:
        raise NotImplementedError

    def _decode_blocks(self, chunk_sections: nbt.TAG_List) -> Tuple[numpy.ndarray, numpy.ndarray]:
        raise NotImplementedError

    def _encode_blocks(self, blocks: numpy.ndarray, palette: numpy.ndarray) -> nbt.TAG_List:
        raise NotImplementedError
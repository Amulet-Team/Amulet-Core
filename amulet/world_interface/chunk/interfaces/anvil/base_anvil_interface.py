from __future__ import annotations

from typing import List, Tuple, Union, Any

import numpy
import amulet_nbt as amulet_nbt

from amulet.api.chunk import Chunk
from amulet.api.block_entity import BlockEntity
from amulet.api.entity import Entity
from amulet.world_interface.chunk.interfaces import Interface
from amulet.world_interface.chunk import translators


class BaseAnvilInterface(Interface):
    def __init__(self):
        feature_options = {
            "data_version": ["int"],  # int
            "last_update": ["long"],  # int
            "status": ["j13", "j14"],
            "light_populated": ["byte"],  # int
            "terrain_populated": ["byte"],  # int
            "V": ["byte"],  # int
            "inhabited_time": ["long"],  # int
            "biomes": ["256BA", "256IA", "1024IA"],  # Biomes
            "height_map": ["256IA", "C5|36LA", "C6|36LA"],
            # 'carving_masks': ['C|?BA'],
            "blocks": ["Sections|(Blocks,Data,Add)", "Sections|(BlockStates,Palette)"],
            "block_light": ["Sections|2048BA"],
            "sky_light": ["Sections|2048BA"],


            "block_entities": ["list"],
            "block_entity_format": ["namespace-str-identifier"],
            "block_entity_coord_format": ["xyz-int"],

            "entities": ["list"],
            "entity_format": ["namespace-str-identifier"],
            "entity_coord_format": ["Pos-list-float"],
            
            
            "tile_ticks": ["list", "list(optional)"],
            "liquid_ticks": ["list"],
            # 'lights': [],
            "liquids_to_be_ticked": ["16list|list"],
            "to_be_ticked": ["16list|list"],
            "post_processing": ["16list|list"],
            "structures": ["compound"],
        }
        self.features = {key: None for key in feature_options.keys()}

    def get_translator(
        self,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        data: amulet_nbt.NBTFile = None,
    ) -> Tuple[translators.Translator, int]:
        if data:
            key, version = ("anvil", data["DataVersion"].value), data["DataVersion"].value
        else:
            key = max_world_version
            version = max_world_version[1]
        return translators.loader.get(key), version

    def decode(self, cx: int, cz: int, data: amulet_nbt.NBTFile) -> Tuple[Chunk, numpy.ndarray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format.
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param data: amulet_nbt.NBTFile
        :return: Chunk object in version-specific format, along with the palette for that chunk.
        """
        misc = {}
        chunk = Chunk(cx, cz)

        if self.features["last_update"] == "long":
            misc["last_update"] = data["Level"]["LastUpdate"].value

        if self.features["status"] in ["j13", "j14"]:
            chunk.status = data["Level"]["Status"].value
        else:
            status = "empty"
            if (
                self.features["terrain_populated"] == "byte"
                and data["Level"]["TerrainPopulated"].value
            ):
                status = "decorated"
            if (
                self.features["light_populated"] == "byte"
                and data["Level"]["LightPopulated"].value
            ):
                status = "postprocessed"

            chunk.status = status

        if self.features["V"] == "byte":
            misc["V"] = data["Level"]["V"].value

        if self.features["inhabited_time"] == "long":
            misc["inhabited_time"] = data["Level"]["InhabitedTime"].value

        if self.features["biomes"] is not None:
            chunk.biomes = data["Level"]["Biomes"].value

        if self.features["height_map"] == "256IA":
            misc["height_map256IA"] = data["Level"]["HeightMap"].value
        elif self.features["height_map"] in ["C5|36LA", "C6|36LA"]:
            misc["height_mapC|36LA"] = data["Level"]["Heightmaps"]

        if self.features["blocks"] in [
            "Sections|(Blocks,Data,Add)",
            "Sections|(BlockStates,Palette)",
        ]:
            chunk.blocks, palette = self._decode_blocks(data["Level"]["Sections"])
        else:
            raise Exception(f'Unsupported block format {self.features["blocks"]}')

        if self.features["block_light"] == "Sections|2048BA":
            misc["block_light"] = {
                section["Y"].value: section["BlockLight"]
                for section in data["Level"]["Sections"]
            }

        if self.features["sky_light"] == "Sections|2048BA":
            misc["sky_light"] = {
                section["Y"].value: section["SkyLight"]
                for section in data["Level"]["Sections"]
            }

        if self.features["entities"] == "list":
            chunk.entities = self._decode_entities(data["Level"].get("Entities", amulet_nbt.TAG_List()))

        if self.features["block_entities"] == "list":
            chunk.block_entities = self._decode_block_entities(data["Level"].get("TileEntities", amulet_nbt.TAG_List()))

        if self.features["tile_ticks"] == "list":
            misc["tile_ticks"] = data["Level"].get("TileTicks", amulet_nbt.TAG_List())

        if self.features["liquid_ticks"] == "list":
            if "LiquidTicks" in data["Level"]:
                misc["liquid_ticks"] = data["Level"]["LiquidTicks"]

        if self.features["liquids_to_be_ticked"] == "16list|list":
            misc["liquids_to_be_ticked"] = data["Level"]["LiquidsToBeTicked"]

        if self.features["to_be_ticked"] == "16list|list":
            misc["to_be_ticked"] = data["Level"]["ToBeTicked"]

        if self.features["post_processing"] == "16list|list":
            misc["post_processing"] = data["Level"]["PostProcessing"]

        if self.features["structures"] == "compound":
            misc["structures"] = data["Level"]["Structures"]

        chunk.misc = misc

        return chunk, palette

    def encode(
        self, chunk: Chunk, palette: numpy.ndarray, max_world_version: Tuple[str, int]
    ) -> amulet_nbt.NBTFile:
        """
        Encode a version-specific chunk to raw data for the format to store.
        :param chunk: The version-specific chunk to translate and encode.
        :param palette: The palette the ids in the chunk correspond to.
        :return: amulet_nbt.NBTFile
        """

        misc = chunk.misc
        data = amulet_nbt.NBTFile(amulet_nbt.TAG_Compound(), "")
        data["Level"] = amulet_nbt.TAG_Compound()
        data["Level"]["xPos"] = amulet_nbt.TAG_Int(chunk.cx)
        data["Level"]["zPos"] = amulet_nbt.TAG_Int(chunk.cz)
        if self.features["data_version"] == "int":
            data["DataVersion"] = amulet_nbt.TAG_Int(max_world_version[1])

        if self.features["last_update"] == "long":
            data["Level"]["LastUpdate"] = amulet_nbt.TAG_Long(misc.get("last_update", 0))

        # TODO: improve this functionality. Perhaps map each one to a float value which is the universal format.
        # Order the float value based on the order they would be run. Newer replacements for the same come just after
        # to save back find the next lowest valid value.
        if self.features["status"] in ["j13", "j14"]:
            status = chunk.status.as_type(self.features["status"])
            data["Level"]["Status"] = amulet_nbt.TAG_String(status)

        else:
            status = chunk.status.as_type('float')
            if self.features["terrain_populated"] == "byte":
                data["Level"]["TerrainPopulated"] = amulet_nbt.TAG_Byte(int(status > -0.3))

            if self.features["light_populated"] == "byte":
                data["Level"]["LightPopulated"] = amulet_nbt.TAG_Byte(int(status > -0.2))

        if self.features["V"] == "byte":
            data["Level"]["V"] = amulet_nbt.TAG_Byte(misc.get("V", 1))

        if self.features["inhabited_time"] == "long":
            data["Level"]["InhabitedTime"] = amulet_nbt.TAG_Long(misc.get("inhabited_time", 0))

        if self.features["biomes"] == "256BA":
            data["Level"]["Biomes"] = amulet_nbt.TAG_Byte_Array(
                chunk.biomes.convert_to_format(256).astype(dtype=numpy.uint8)
            )
        elif self.features["biomes"] == "256IA":
            data["Level"]["Biomes"] = amulet_nbt.TAG_Int_Array(
                chunk.biomes.convert_to_format(256).astype(dtype=numpy.uint32)
            )
        elif self.features["biomes"] == "1024IA":
            data["Level"]["Biomes"] = amulet_nbt.TAG_Int_Array(
                chunk.biomes.convert_to_format(1024).astype(dtype=numpy.uint32)
            )

        if self.features["height_map"] == "256IA":
            data["Level"]["HeightMap"] = amulet_nbt.TAG_Int_Array(
                misc.get("height_map256IA", numpy.zeros(256, dtype=numpy.uint32))
            )
        elif self.features["height_map"] in ["C6|36LA", "C5|36LA"]:
            if self.features["height_map"] == "C5|36LA":
                maps = (
                    "LIGHT_BLOCKING",
                    "MOTION_BLOCKING",
                    "MOTION_BLOCKING_NO_LEAVES",
                    "OCEAN_FLOOR",
                    "WORLD_SURFACE",
                )
            elif self.features["height_map"] == "C6|36LA":
                maps = (
                    "MOTION_BLOCKING",
                    "MOTION_BLOCKING_NO_LEAVES",
                    "OCEAN_FLOOR",
                    "OCEAN_FLOOR_WG",
                    "WORLD_SURFACE",
                    "WORLD_SURFACE_WG",
                )
            else:
                raise Exception
            heightmaps = misc.get("height_mapC|36LA", amulet_nbt.TAG_Compound())
            for heightmap in maps:
                if heightmap not in heightmaps:
                    heightmaps[heightmap] = amulet_nbt.TAG_Long_Array(
                        numpy.zeros(36, dtype=">i8")
                    )
            data["Level"]["Heightmaps"] = heightmaps

        if self.features["blocks"] in [
            "Sections|(Blocks,Data,Add)",
            "Sections|(BlockStates,Palette)",
        ]:
            data["Level"]["Sections"] = self._encode_blocks(chunk.blocks, palette)
        else:
            raise Exception(f'Unsupported block format {self.features["blocks"]}')

        if self.features["block_light"] in ["Sections|2048BA"] or self.features[
            "sky_light"
        ] in ["Sections|2048BA"]:
            for section in data["Level"]["Sections"]:
                y = section["Y"].value
                if self.features["block_light"] == "Sections|2048BA":
                    block_light = misc.get("block_light", {})
                    if y in block_light:
                        section["BlockLight"] = block_light[y]
                    else:
                        section["BlockLight"] = amulet_nbt.TAG_Byte_Array(
                            numpy.full(2048, 255, dtype=numpy.uint8)
                        )
                if self.features["sky_light"] == "Sections|2048BA":
                    sky_light = misc.get("sky_light", {})
                    if y in sky_light:
                        section["SkyLight"] = sky_light[y]
                    else:
                        section["SkyLight"] = amulet_nbt.TAG_Byte_Array(
                            numpy.full(2048, 255, dtype=numpy.uint8)
                        )

        if self.features["entities"] == "list":
            data["Level"]["Entities"] = self._encode_entities(chunk.entities)

        if self.features["tile_ticks"] in ["list", "list(optional)"]:
            ticks = misc.get("tile_ticks", amulet_nbt.TAG_List())
            if self.features["tile_ticks"] == "list(optional)":
                if len(ticks) > 0:
                    data["Level"]["TileTicks"] = ticks
            elif self.features["tile_ticks"] == "list":
                data["Level"]["TileTicks"] = ticks

        if self.features["liquid_ticks"] == "list":
            data["Level"]["LiquidTicks"] = misc.get(
                "liquid_ticks", amulet_nbt.TAG_List()
            )

        if self.features["liquids_to_be_ticked"] == "16list|list":
            data["Level"]["LiquidsToBeTicked"] = misc.get(
                "liquids_to_be_ticked",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self.features["to_be_ticked"] == "16list|list":
            data["Level"]["ToBeTicked"] = misc.get(
                "to_be_ticked", amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)])
            )

        if self.features["post_processing"] == "16list|list":
            data["Level"]["PostProcessing"] = misc.get(
                "post_processing", amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)])
            )

        if self.features["structures"] == "compound":
            data["Level"]["Structures"] = misc.get(
                "structures",
                amulet_nbt.TAG_Compound(
                    {"References": amulet_nbt.TAG_Compound(), "Starts": amulet_nbt.TAG_Compound()}
                ),
            )

        return data

    def _decode_entities(self, entities: amulet_nbt.TAG_List) -> List[Entity]:
        entities_out = []
        if self.features['entity_format'] == 'namespace-str-id':
            if self.features['entity_coord_format'] == "Pos-list-float":
                for nbt in entities:
                    entity_name, (x, y, z) = [nbt.pop(key).value for key in ['id', 'Pos']]
                    namespace, base_name = entity_name.split(':', 1)
                    entities_out.append(Entity(namespace=namespace, base_name=base_name, x=x, y=y, z=z, nbt=nbt))

        elif self.features['entity_format'] == 'str-id':  # I don't think this was ever a thing on Java
            if self.features['entity_coord_format'] == "Pos-list-float":
                for nbt in entities:
                    base_name, (x, y, z) = [nbt.pop(key).value for key in ['id', 'Pos']]
                    entities_out.append(Entity(namespace=None, base_name=base_name, x=x, y=y, z=z, nbt=nbt))
        return entities_out

    def _encode_entities(self, entities: List[BlockEntity]) -> amulet_nbt.TAG_List:
        return amulet_nbt.TAG_List([])

    def _decode_block_entities(self, block_entities: amulet_nbt.TAG_List) -> List[BlockEntity]:
        block_entities_out = []
        if self.features['block_entity_format'] == 'namespace-str-id':
            if self.features['block_entity_coord_format'] == "xyz-int":
                for nbt in block_entities:
                    block_entity_name, x, y, z = [nbt.pop(key).value for key in ['id', 'x', 'y', 'z']]
                    namespace, base_name = block_entity_name.split(':', 1)
                    block_entities_out.append(BlockEntity(namespace=namespace, base_name=base_name, x=x, y=y, z=z, nbt=nbt))

        elif self.features['block_entity_format'] == 'str-id':
            if self.features['block_entity_coord_format'] == 'xyz-int':
                for nbt in block_entities:
                    base_name, x, y, z = [nbt.pop(key).value for key in ['id', 'x', 'y', 'z']]
                    block_entities_out.append(BlockEntity(namespace=None, base_name=base_name, x=x, y=y, z=z, nbt=nbt))
        return block_entities_out

    def _encode_block_entities(self, block_entities: List[BlockEntity]) -> amulet_nbt.TAG_List:
        return amulet_nbt.TAG_List([])

    def _decode_blocks(
        self, chunk_sections: amulet_nbt.TAG_List
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        raise NotImplementedError

    def _encode_blocks(
        self, blocks: numpy.ndarray, palette: numpy.ndarray
    ) -> amulet_nbt.TAG_List:
        raise NotImplementedError

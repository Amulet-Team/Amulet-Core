from __future__ import annotations

from typing import List, Tuple, Union, Iterable, Dict, TYPE_CHECKING
import numpy

import amulet_nbt as amulet_nbt

import amulet
from amulet.api.chunk import Chunk
from amulet.api.block import Block
from amulet.api.wrapper import Interface
from amulet.world_interface.chunk import translators
from amulet.api.data_types import AnyNDArray, SubChunkNDArray

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity
    from amulet.api.chunk.blocks import Blocks


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
            "height_map": ["256IA", "C|36LA|V1", "C|36LA|V2", "C|36LA|V3", "C|36LA|V4"],
            # 'carving_masks': ['C|?BA'],
            "blocks": ["Sections|(Blocks,Data,Add)", "Sections|(BlockStates,Palette)"],
            "long_array_format": [
                "compact",
                "1.16",
            ],  # before the long array was just a bit stream but it is now separete longs. The upper bits are unused in some cases.
            "block_light": ["Sections|2048BA"],
            "sky_light": ["Sections|2048BA"],
            "block_entities": ["list"],
            "block_entity_format": ["namespace-str-id"],
            "block_entity_coord_format": ["xyz-int"],
            "entities": ["list"],
            "entity_format": ["namespace-str-id"],
            "entity_coord_format": ["Pos-list-double"],
            "tile_ticks": ["list", "list(optional)"],
            "liquid_ticks": ["list"],
            # 'lights': [],
            "liquids_to_be_ticked": ["16list|list"],
            "to_be_ticked": ["16list|list"],
            "post_processing": ["16list|list"],
            "structures": ["compound"],
        }
        self.features = {key: None for key in feature_options.keys()}

    def is_valid(self, key: Tuple) -> bool:
        return key[0] == "java" and self.minor_is_valid(key[1])

    @staticmethod
    def minor_is_valid(key: int):
        raise NotImplementedError

    def get_translator(
        self,
        max_world_version: Tuple[str, Union[int, Tuple[int, int, int]]],
        data: amulet_nbt.NBTFile = None,
    ) -> Tuple["Translator", int]:
        if data:
            data_version = data.get("DataVersion", amulet_nbt.TAG_Int(-1)).value
            key, version = (("java", data_version), data_version)
        else:
            key = max_world_version
            version = max_world_version[1]
        return translators.loader.get(key), version

    def decode(
        self, cx: int, cz: int, data: amulet_nbt.NBTFile
    ) -> Tuple["Chunk", AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format.
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param data: amulet_nbt.NBTFile
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
        misc = {}
        chunk = Chunk(cx, cz)

        if self.features["last_update"] == "long":
            misc["last_update"] = (
                data["Level"].get("LastUpdate", amulet_nbt.TAG_Long(0)).value
            )

        if self.features["status"] in ["j13", "j14"]:
            chunk.status = data["Level"]["Status"].value
        else:
            status = "empty"
            if (
                self.features["terrain_populated"] == "byte"
                and data["Level"].get("TerrainPopulated", amulet_nbt.TAG_Byte()).value
            ):
                status = "decorated"
            if (
                self.features["light_populated"] == "byte"
                and data["Level"].get("LightPopulated", amulet_nbt.TAG_Byte()).value
            ):
                status = "postprocessed"

            chunk.status = status

        if self.features["V"] == "byte":
            misc["V"] = data["Level"]["V"].value

        if self.features["inhabited_time"] == "long":
            misc["inhabited_time"] = (
                data["Level"].get("InhabitedTime", amulet_nbt.TAG_Long(0)).value
            )

        if self.features["biomes"] is not None:
            if "Biomes" in data["Level"]:
                biomes = data["Level"]["Biomes"].value
                if self.features["biomes"] in ["256BA", "256IA"]:
                    chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))
                elif self.features["biomes"] == "1024IA":
                    chunk.biomes = {
                        sy: arr
                        for sy, arr in enumerate(
                            numpy.split(
                                numpy.transpose(
                                    biomes.astype(numpy.uint32).reshape(64, 4, 4),
                                    (2, 0, 1),
                                ),  # YZX -> XYZ
                                16,
                                1,
                            )
                        )
                    }

        if self.features["height_map"] == "256IA":
            misc["height_map256IA"] = data["Level"]["HeightMap"].value
        elif self.features["height_map"] in [
            "C|36LA|V1",
            "C|36LA|V2",
            "C|36LA|V3",
            "C|36LA|V4",
        ]:
            if "Heightmaps" in data["Level"]:
                misc["height_mapC|36LA"] = data["Level"]["Heightmaps"]

        if "Sections" in data["Level"]:
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
                    if "BlockLight" in section
                }

            if self.features["sky_light"] == "Sections|2048BA":
                misc["sky_light"] = {
                    section["Y"].value: section["SkyLight"]
                    for section in data["Level"]["Sections"]
                    if "SkyLight" in section
                }
        else:
            palette = numpy.array([Block(namespace="minecraft", base_name="air")])

        if self.features["entities"] == "list":
            if amulet.entity_support:
                chunk.entities = self._decode_entities(
                    data["Level"].get("Entities", amulet_nbt.TAG_List())
                )
            else:
                misc["java_entities_temp"] = self._decode_entities(
                    data["Level"].get("Entities", amulet_nbt.TAG_List())
                )

        if self.features["block_entities"] == "list":
            chunk.block_entities = self._decode_block_entities(
                data["Level"].get("TileEntities", amulet_nbt.TAG_List())
            )

        if self.features["tile_ticks"] == "list":
            misc["tile_ticks"] = data["Level"].get("TileTicks", amulet_nbt.TAG_List())

        if self.features["liquid_ticks"] == "list":
            if "LiquidTicks" in data["Level"]:
                misc["liquid_ticks"] = data["Level"]["LiquidTicks"]

        if self.features["liquids_to_be_ticked"] == "16list|list":
            if "LiquidsToBeTicked" in data["Level"]:
                misc["liquids_to_be_ticked"] = data["Level"]["LiquidsToBeTicked"]

        if self.features["to_be_ticked"] == "16list|list":
            if "ToBeTicked" in data["Level"]:
                misc["to_be_ticked"] = data["Level"]["ToBeTicked"]

        if self.features["post_processing"] == "16list|list":
            if "PostProcessing" in data["Level"]:
                misc["post_processing"] = data["Level"]["PostProcessing"]

        if self.features["structures"] == "compound":
            if "Structures" in data["Level"]:
                misc["structures"] = data["Level"]["Structures"]

        chunk.misc = misc

        return chunk, palette

    def encode(
        self, chunk: "Chunk", palette: AnyNDArray, max_world_version: Tuple[str, int]
    ) -> amulet_nbt.NBTFile:
        """
        Encode a version-specific chunk to raw data for the format to store.
        :param chunk: The version-specific chunk to translate and encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :param max_world_version: The key to use to find the encoder.
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
            data["Level"]["LastUpdate"] = amulet_nbt.TAG_Long(
                misc.get("last_update", 0)
            )

        # Order the float value based on the order they would be run. Newer replacements for the same come just after
        # to save back find the next lowest valid value.
        if self.features["status"] in ["j13", "j14"]:
            status = chunk.status.as_type(self.features["status"])
            data["Level"]["Status"] = amulet_nbt.TAG_String(status)

        else:
            status = chunk.status.as_type("float")
            if self.features["terrain_populated"] == "byte":
                data["Level"]["TerrainPopulated"] = amulet_nbt.TAG_Byte(
                    int(status > -0.3)
                )

            if self.features["light_populated"] == "byte":
                data["Level"]["LightPopulated"] = amulet_nbt.TAG_Byte(
                    int(status > -0.2)
                )

        if self.features["V"] == "byte":
            data["Level"]["V"] = amulet_nbt.TAG_Byte(misc.get("V", 1))

        if self.features["inhabited_time"] == "long":
            data["Level"]["InhabitedTime"] = amulet_nbt.TAG_Long(
                misc.get("inhabited_time", 0)
            )

        if self.features["biomes"] == "256BA":  # TODO: support the optional variant
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_2d()
                data["Level"]["Biomes"] = amulet_nbt.TAG_Byte_Array(
                    chunk.biomes.astype(dtype=numpy.uint8)
                )
        elif self.features["biomes"] == "256IA":
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_2d()
                data["Level"]["Biomes"] = amulet_nbt.TAG_Int_Array(
                    chunk.biomes.astype(dtype=numpy.uint32)
                )
        elif self.features["biomes"] == "1024IA":
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_3d()
                data["Level"]["Biomes"] = amulet_nbt.TAG_Int_Array(
                    numpy.transpose(
                        numpy.asarray(chunk.biomes[:, 0:64, :]).astype(numpy.uint32),
                        (1, 2, 0),
                    ).ravel(),  # YZX -> XYZ
                )

        if self.features["height_map"] == "256IA":
            data["Level"]["HeightMap"] = amulet_nbt.TAG_Int_Array(
                misc.get("height_map256IA", numpy.zeros(256, dtype=numpy.uint32))
            )
        elif self.features["height_map"] in [
            "C|36LA|V1",
            "C|36LA|V2",
            "C|36LA|V3",
            "C|36LA|V4",
        ]:
            maps = [
                "WORLD_SURFACE_WG",
                "OCEAN_FLOOR_WG",
                "MOTION_BLOCKING",
                "MOTION_BLOCKING_NO_LEAVES",
                "OCEAN_FLOOR",
            ]
            if self.features["height_map"] == "C|36LA|V1":  # 1466
                maps = ("LIQUID", "SOILD", "LIGHT", "RAIN")
            elif self.features["height_map"] == "C|36LA|V2":  # 1484
                maps.append("LIGHT_BLOCKING")
            elif self.features["height_map"] == "C|36LA|V3":  # 1503
                maps.append("LIGHT_BLOCKING")
                maps.append("WORLD_SURFACE")
            elif self.features["height_map"] == "C|36LA|V4":  # 1908
                maps.append("WORLD_SURFACE")
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
            if amulet.entity_support:
                data["Level"]["Entities"] = self._encode_entities(chunk.entities)
            else:
                data["Level"]["Entities"] = self._encode_entities(
                    misc.get("java_entities_temp", amulet_nbt.TAG_List())
                )

        if self.features["block_entities"] == "list":
            data["Level"]["TileEntities"] = self._encode_block_entities(
                chunk.block_entities
            )

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
                "to_be_ticked",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self.features["post_processing"] == "16list|list":
            data["Level"]["PostProcessing"] = misc.get(
                "post_processing",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self.features["structures"] == "compound":
            data["Level"]["Structures"] = misc.get(
                "structures",
                amulet_nbt.TAG_Compound(
                    {
                        "References": amulet_nbt.TAG_Compound(),
                        "Starts": amulet_nbt.TAG_Compound(),
                    }
                ),
            )

        return data

    def _decode_entities(self, entities: amulet_nbt.TAG_List) -> List["Entity"]:
        entities_out = []
        for nbt in entities:
            entity = self._decode_entity(
                amulet_nbt.NBTFile(nbt),
                self.features["entity_format"],
                self.features["entity_coord_format"],
            )
            if entity is not None:
                entities_out.append(entity)

        return entities_out

    def _encode_entities(self, entities: Iterable["Entity"]) -> amulet_nbt.TAG_List:
        entities_out = []
        for entity in entities:
            nbt = self._encode_entity(
                entity,
                self.features["entity_format"],
                self.features["entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt.value)

        return amulet_nbt.TAG_List(entities_out)

    def _decode_block_entities(
        self, block_entities: amulet_nbt.TAG_List
    ) -> List["BlockEntity"]:
        entities_out = []
        for nbt in block_entities:
            entity = self._decode_block_entity(
                amulet_nbt.NBTFile(nbt),
                self.features["block_entity_format"],
                self.features["block_entity_coord_format"],
            )
            if entity is not None:
                entities_out.append(entity)

        return entities_out

    def _encode_block_entities(
        self, block_entities: Iterable["BlockEntity"]
    ) -> amulet_nbt.TAG_List:
        entities_out = []
        for entity in block_entities:
            nbt = self._encode_block_entity(
                entity,
                self.features["block_entity_format"],
                self.features["block_entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt.value)

        return amulet_nbt.TAG_List(entities_out)

    def _decode_blocks(
        self, chunk_sections: amulet_nbt.TAG_List
    ) -> Tuple[Dict[int, SubChunkNDArray], AnyNDArray]:
        raise NotImplementedError

    def _encode_blocks(
        self, blocks: "Blocks", palette: AnyNDArray
    ) -> amulet_nbt.TAG_List:
        raise NotImplementedError

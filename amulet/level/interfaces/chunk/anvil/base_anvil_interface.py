from __future__ import annotations

from typing import List, Tuple, Union, Iterable, Dict, TYPE_CHECKING, Optional
import numpy

import amulet_nbt
from amulet_nbt import (
    TAG_Byte,
    TAG_Int,
    TAG_Long,
    TAG_Byte_Array,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Int_Array,
    TAG_Long_Array,
    NBTFile,
)

import amulet
from amulet import log
from amulet.api.chunk import Chunk, StatusFormats
from amulet.api.wrapper import Interface
from amulet.level import loader
from amulet.api.data_types import AnyNDArray, SubChunkNDArray
from amulet.api.wrapper import EntityIDType, EntityCoordType
from amulet.utils.world_utils import decode_long_array, encode_long_array

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
            "height_map": [
                "256IARequired",  # A 256 element Int Array in HeightMap
                "256IA",  # A 256 element Int Array in HeightMap
                "C|V1",  # A Compound of Long Arrays with these keys "LIQUID", "SOILD", "LIGHT", "RAIN"
                "C|V2",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "LIGHT_BLOCKING"
                "C|V3",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "LIGHT_BLOCKING", "WORLD_SURFACE"
                "C|V4",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "WORLD_SURFACE"
            ],
            # 'carving_masks': ['C|?BA'],
            "blocks": ["Sections|(Blocks,Data,Add)", "Sections|(BlockStates,Palette)"],
            "long_array_format": [
                "compact",
                "1.16",
            ],  # before the long array was just a bit stream but it is now separete longs. The upper bits are unused in some cases.
            "block_light": ["Sections|2048BA"],
            "sky_light": ["Sections|2048BA"],
            "light_optional": ["false", "true"],
            "block_entities": ["list"],
            "block_entity_format": [EntityIDType.namespace_str_id],
            "block_entity_coord_format": [EntityCoordType.xyz_int],
            "entities": ["list"],
            "entity_format": [EntityIDType.namespace_str_id],
            "entity_coord_format": [EntityCoordType.Pos_list_double],
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
        return loader.Translators.get(key), version

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
        misc = {
            # store the chunk data so that any non-versioned data can get saved back
            "java_chunk_data": data
        }
        # all versioned data must get removed from data

        chunk = Chunk(cx, cz)

        if "DataVersion" in data:
            del data["DataVersion"]

        # make sure this exists otherwise the code below will error.
        level = data.value.setdefault("Level", amulet_nbt.TAG_Compound())

        if self.features["last_update"] == "long":
            misc["last_update"] = self.get_obj(level, "LastUpdate", TAG_Long).value

        if self.features["status"] in [StatusFormats.Java_13, StatusFormats.Java_14]:
            chunk.status = self.get_obj(
                level, "Status", TAG_String, TAG_String("full")
            ).value
        else:
            status = "empty"
            if self.features["terrain_populated"] == "byte" and self.get_obj(
                level, "TerrainPopulated", TAG_Byte
            ):
                status = "decorated"
            if self.features["light_populated"] == "byte" and self.get_obj(
                level, "LightPopulated", TAG_Byte
            ):
                status = "postprocessed"

            chunk.status = status

        if self.features["V"] == "byte":
            misc["V"] = self.get_obj(level, "V", TAG_Byte, TAG_Byte(1)).value

        if self.features["inhabited_time"] == "long":
            misc["inhabited_time"] = self.get_obj(
                level, "InhabitedTime", TAG_Long
            ).value

        if self.features["biomes"] is not None:
            if "Biomes" in level:
                biomes = level.pop("Biomes")
                if self.features["biomes"] == "256BA":
                    if isinstance(biomes, TAG_Byte_Array) and biomes.value.size == 256:
                        chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))
                elif self.features["biomes"] == "256IA":
                    if isinstance(biomes, TAG_Int_Array) and biomes.value.size == 256:
                        chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))
                elif self.features["biomes"] == "1024IA":
                    if isinstance(biomes, TAG_Int_Array) and biomes.value.size == 1024:
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

        if self.features["height_map"] in ["256IA", "256IARequired"]:
            height = self.get_obj(level, "HeightMap", TAG_Int_Array).value
            if isinstance(height, numpy.ndarray) and height.size == 256:
                misc["height_map256IA"] = height.reshape((16, 16))
        elif self.features["height_map"] in ["C|V1", "C|V2", "C|V3", "C|V4"]:
            heights = self.get_obj(level, "Heightmaps", TAG_Compound)
            misc["height_mapC"] = {
                key: decode_long_array(value, 256, len(value) == 36).reshape((16, 16))
                for key, value in heights.items()
                if isinstance(value, TAG_Long_Array)
            }

        # parse sections into a more usable format
        sections: Dict[int, TAG_Compound] = {
            section.pop("Y").value: section
            for section in self.get_obj(level, "Sections", TAG_List)
            if isinstance(section, TAG_Compound)
            and self.check_type(section, "Y", TAG_Byte)
        }
        misc["java_sections"] = sections

        if self.features["blocks"] in [
            "Sections|(Blocks,Data,Add)",
            "Sections|(BlockStates,Palette)",
        ]:
            chunk.blocks, palette = self._decode_blocks(sections)
        else:
            raise Exception(f'Unsupported block format {self.features["blocks"]}')

        def unpack_light(feature_key: str, section_key: str):
            if self.features[feature_key] == "Sections|2048BA":
                misc[feature_key] = light_container = {}
                for cy, section in sections.items():
                    if self.check_type(section, section_key, TAG_Byte_Array):
                        light: numpy.ndarray = section.pop(section_key).value
                        if light.size == 2048:
                            # TODO: check if this needs transposing or if the values are the other way around
                            light_container[cy] = (
                                (
                                    light.reshape(-1, 1)
                                    & numpy.array([0xF, 0xF0], dtype=numpy.uint8)
                                )
                                >> numpy.array([0, 4], dtype=numpy.uint8)
                            ).reshape((16, 16, 16))

        unpack_light("block_light", "BlockLight")
        unpack_light("sky_light", "SkyLight")

        if self.features["entities"] == "list":
            ents = self._decode_entities(self.get_obj(level, "Entities", TAG_List))
            if amulet.entity_support:
                chunk.entities = ents
            else:
                misc["java_entities_temp"] = ents

        if self.features["block_entities"] == "list":
            chunk.block_entities = self._decode_block_entities(
                self.get_obj(level, "TileEntities", TAG_List)
            )

        if self.features["tile_ticks"] == "list":
            misc["tile_ticks"] = self.get_obj(level, "TileTicks", TAG_List)

        if self.features["liquid_ticks"] == "list":
            misc["liquid_ticks"] = self.get_obj(level, "LiquidTicks", TAG_List)

        if self.features["liquids_to_be_ticked"] == "16list|list":
            misc["liquids_to_be_ticked"] = self.get_obj(
                level, "LiquidsToBeTicked", TAG_List
            )

        if self.features["to_be_ticked"] == "16list|list":
            misc["to_be_ticked"] = self.get_obj(level, "ToBeTicked", TAG_List)

        if self.features["post_processing"] == "16list|list":
            misc["post_processing"] = self.get_obj(level, "PostProcessing", TAG_List)

        if self.features["structures"] == "compound":
            misc["structures"] = self.get_obj(level, "Structures", TAG_Compound)

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
        if "java_chunk_data" in misc and isinstance(misc["java_chunk_data"], NBTFile):
            data = misc["java_chunk_data"]
        else:
            data = NBTFile()
        level: TAG_Compound = self.set_obj(data, "Level", TAG_Compound)
        level["xPos"] = TAG_Int(chunk.cx)
        level["zPos"] = TAG_Int(chunk.cz)
        if self.features["data_version"] == "int":
            data["DataVersion"] = amulet_nbt.TAG_Int(max_world_version[1])
        elif "DataVersion" in data:
            del data["DataVersion"]

        if self.features["last_update"] == "long":
            level["LastUpdate"] = amulet_nbt.TAG_Long(misc.get("last_update", 0))

        # Order the float value based on the order they would be run. Newer replacements for the same come just after
        # to save back find the next lowest valid value.
        if self.features["status"] in [StatusFormats.Java_13, StatusFormats.Java_14]:
            status = chunk.status.as_type(self.features["status"])
            level["Status"] = amulet_nbt.TAG_String(status)

        else:
            status = chunk.status.as_type(StatusFormats.Raw)
            if self.features["terrain_populated"] == "byte":
                level["TerrainPopulated"] = amulet_nbt.TAG_Byte(int(status > -0.3))

            if self.features["light_populated"] == "byte":
                level["LightPopulated"] = amulet_nbt.TAG_Byte(int(status > -0.2))

        if self.features["V"] == "byte":
            level["V"] = amulet_nbt.TAG_Byte(misc.get("V", 1))

        if self.features["inhabited_time"] == "long":
            level["InhabitedTime"] = amulet_nbt.TAG_Long(misc.get("inhabited_time", 0))

        if self.features["biomes"] == "256BA":  # TODO: support the optional variant
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_2d()
                level["Biomes"] = amulet_nbt.TAG_Byte_Array(
                    chunk.biomes.astype(dtype=numpy.uint8)
                )
        elif self.features["biomes"] == "256IA":
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_2d()
                level["Biomes"] = amulet_nbt.TAG_Int_Array(
                    chunk.biomes.astype(dtype=numpy.uint32)
                )
        elif self.features["biomes"] == "1024IA":
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_3d()
                level["Biomes"] = amulet_nbt.TAG_Int_Array(
                    numpy.transpose(
                        numpy.asarray(chunk.biomes[:, 0:64, :]).astype(numpy.uint32),
                        (1, 2, 0),
                    ).ravel()  # YZX -> XYZ
                )

        if self.features["height_map"] in ["256IA", "256IARequired"]:
            height = misc.get("height_map256IA", None)
            if (
                isinstance(height, numpy.ndarray)
                and numpy.issubdtype(height.dtype, numpy.integer)
                and height.shape == (16, 16)
            ):
                level["HeightMap"] = amulet_nbt.TAG_Int_Array(height.ravel())
            elif self.features["height_map"] == "256IARequired":
                level["HeightMap"] = amulet_nbt.TAG_Int_Array(
                    numpy.zeros(256, dtype=numpy.uint32)
                )
        elif self.features["height_map"] in {"C|V1", "C|V2", "C|V3", "C|V4"}:
            maps = [
                "WORLD_SURFACE_WG",
                "OCEAN_FLOOR_WG",
                "MOTION_BLOCKING",
                "MOTION_BLOCKING_NO_LEAVES",
                "OCEAN_FLOOR",
            ]
            if self.features["height_map"] == "C|V1":  # 1466
                maps = ("LIQUID", "SOILD", "LIGHT", "RAIN")
            elif self.features["height_map"] == "C|V2":  # 1484
                maps.append("LIGHT_BLOCKING")
            elif self.features["height_map"] == "C|V3":  # 1503
                maps.append("LIGHT_BLOCKING")
                maps.append("WORLD_SURFACE")
            elif self.features["height_map"] == "C|V4":  # 1908
                maps.append("WORLD_SURFACE")
            else:
                raise Exception
            heightmaps_temp: Dict[str, numpy.ndarray] = misc.get("height_mapC", {})
            heightmaps = amulet_nbt.TAG_Compound()
            heightmap_length = (
                36 if max_world_version[1] < 2556 else 37
            )  # this value is probably actually much lower
            for heightmap in maps:
                value: Optional[amulet_nbt.TAG_Long_Array] = None
                if heightmap in heightmaps_temp and isinstance(
                    heightmaps_temp[heightmap], numpy.ndarray
                ):
                    array = encode_long_array(
                        heightmaps_temp[heightmap].ravel(),
                        max_world_version[1] < 2556,
                        9,
                    )
                    if array.size == heightmap_length:
                        value = amulet_nbt.TAG_Long_Array(array)
                    else:
                        log.error(
                            f"Expected an array of length {heightmap_length} but got an array of length {array.size}"
                        )
                if value is not None:
                    heightmaps[heightmap] = value
            level["Heightmaps"] = heightmaps

        if "java_sections" in misc and isinstance(misc["java_sections"], dict):
            # verify that the data is correctly formatted.
            sections = {
                cy: section
                for cy, section in misc["java_sections"].items()
                if isinstance(cy, int) and isinstance(section, TAG_Compound)
            }
        else:
            sections = {}

        if self.features["blocks"] in [
            "Sections|(Blocks,Data,Add)",
            "Sections|(BlockStates,Palette)",
        ]:
            self._encode_blocks(sections, chunk.blocks, palette)
        else:
            raise Exception(f'Unsupported block format {self.features["blocks"]}')

        def pack_light(feature_key: str, section_key: str):
            if self.features[feature_key] == "Sections|2048BA":
                light_container = misc.get(feature_key, {})
                if not isinstance(light_container, dict):
                    light_container = {}
                for cy, section in sections.items():
                    light = light_container.get(cy, None)
                    if (
                        isinstance(light, numpy.ndarray)
                        and numpy.issubdtype(light.dtype, numpy.integer)
                        and light.shape == (16, 16, 16)
                    ):
                        light = light.ravel() % 16
                        section[section_key] = amulet_nbt.TAG_Byte_Array(
                            light[::2] + (light[1::2] << 4)
                        )
                    elif self.features["light_optional"] == "false":
                        section[section_key] = amulet_nbt.TAG_Byte_Array(
                            numpy.full(2048, 255, dtype=numpy.uint8)
                        )

        pack_light("block_light", "BlockLight")
        pack_light("sky_light", "SkyLight")

        sections_list = []
        for cy, section in sections.items():
            section["Y"] = TAG_Byte(cy)
            sections_list.append(section)
        level["Sections"] = TAG_List(sections_list)

        if self.features["entities"] == "list":
            if amulet.entity_support:
                level["Entities"] = self._encode_entities(chunk.entities)
            else:
                level["Entities"] = self._encode_entities(
                    misc.get("java_entities_temp", amulet_nbt.TAG_List())
                )

        if self.features["block_entities"] == "list":
            level["TileEntities"] = self._encode_block_entities(chunk.block_entities)

        if self.features["tile_ticks"] in ["list", "list(optional)"]:
            ticks = misc.get("tile_ticks", amulet_nbt.TAG_List())
            if self.features["tile_ticks"] == "list(optional)":
                if len(ticks) > 0:
                    level["TileTicks"] = ticks
            elif self.features["tile_ticks"] == "list":
                level["TileTicks"] = ticks

        if self.features["liquid_ticks"] == "list":
            level["LiquidTicks"] = misc.get("liquid_ticks", amulet_nbt.TAG_List())

        if self.features["liquids_to_be_ticked"] == "16list|list":
            level["LiquidsToBeTicked"] = misc.get(
                "liquids_to_be_ticked",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self.features["to_be_ticked"] == "16list|list":
            level["ToBeTicked"] = misc.get(
                "to_be_ticked",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self.features["post_processing"] == "16list|list":
            level["PostProcessing"] = misc.get(
                "post_processing",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self.features["structures"] == "compound":
            level["Structures"] = misc.get(
                "structures",
                amulet_nbt.TAG_Compound(
                    {
                        "References": amulet_nbt.TAG_Compound(),
                        "Starts": amulet_nbt.TAG_Compound(),
                    }
                ),
            )

        return data

    def _decode_entities(self, entities: TAG_List) -> List["Entity"]:
        entities_out = []
        if entities.list_data_type == TAG_Compound.tag_id:
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

    def _decode_block_entities(self, block_entities: TAG_List) -> List["BlockEntity"]:
        entities_out = []
        if block_entities.list_data_type == TAG_Compound.tag_id:
            for nbt in block_entities:
                if not isinstance(nbt, TAG_Compound):
                    continue
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
        self, chunk_sections: Dict[int, TAG_Compound]
    ) -> Tuple[Dict[int, SubChunkNDArray], AnyNDArray]:
        raise NotImplementedError

    def _encode_blocks(
        self, sections: Dict[int, TAG_Compound], blocks: "Blocks", palette: AnyNDArray
    ):
        raise NotImplementedError

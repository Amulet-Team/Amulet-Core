from __future__ import annotations

from typing import List, Tuple, Iterable, Dict, TYPE_CHECKING, Any
import numpy


import amulet_nbt
from amulet_nbt import (
    TAG_Byte,
    TAG_Int,
    TAG_Long,
    TAG_Byte_Array,
    TAG_List,
    TAG_Compound,
    TAG_Int_Array,
    NBTFile,
)

import amulet
from amulet.api.chunk import Chunk, StatusFormats
from amulet.api.wrapper import Interface
from amulet.level import loader
from amulet.api.data_types import AnyNDArray, VersionIdentifierType
from amulet.api.wrapper import EntityIDType, EntityCoordType
from amulet.utils.world_utils import encode_long_array
from .feature_enum import BiomeState, HeightState

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity
    from amulet.api.chunk.blocks import Blocks


class BaseAnvilInterface(Interface):
    def __init__(self):
        self._feature_options = {
            "data_version": ["int"],  # int
            "last_update": ["long"],  # int
            "status": StatusFormats,
            "light_populated": ["byte"],  # int
            "terrain_populated": ["byte"],  # int
            "V": ["byte"],  # int
            "inhabited_time": ["long"],  # int
            "biomes": BiomeState,  # Biomes
            "height_state": HeightState,  # The height of the chunk
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
        self._features = {key: None for key in self._feature_options.keys()}

    def _set_feature(self, feature: str, option: Any):
        assert feature in self._feature_options, f"{feature} is not a valid feature."
        assert (
            option in self._feature_options[feature]
        ), f'Invalid option {option} for feature "{feature}"'
        self._features[feature] = option

    def is_valid(self, key: Tuple) -> bool:
        return key[0] == "java" and self.minor_is_valid(key[1])

    @staticmethod
    def minor_is_valid(key: int):
        raise NotImplementedError

    def get_translator(
        self,
        max_world_version: VersionIdentifierType,
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
        self, cx: int, cz: int, nbt_file: NBTFile, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data.
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param nbt_file: amulet_nbt.NBTFile
        :param bounds: The minimum and maximum bounds of the chunk. In 1.17 this is required to define where the biome array sits.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
        raise NotImplementedError

    @staticmethod
    def _init_decode(cx: int, cz: int, data: NBTFile) -> Tuple[Chunk, TAG_Compound]:
        """Get the decode started by creating a chunk object."""
        chunk = Chunk(cx, cz)
        assert isinstance(data.value, TAG_Compound), "Raw data must be a compound."
        chunk.misc = {
            # store the chunk data so that any non-versioned data can get saved back
            "java_chunk_data": data.value
        }
        return chunk, data.value

    @staticmethod
    def _remove_data_version(compound: TAG_Compound):
        # all versioned data must get removed from data
        if "DataVersion" in compound.value:
            del compound["DataVersion"]

    def _decode_last_update(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["last_update"] = self.get_obj(compound, "LastUpdate", TAG_Long).value

    def _decode_status(self, chunk: Chunk, compound: TAG_Compound):
        raise NotImplementedError

    def _decode_v_tag(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["V"] = self.get_obj(compound, "V", TAG_Byte, TAG_Byte(1)).value

    def _decode_inhabited_time(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["inhabited_time"] = self.get_obj(
            compound, "InhabitedTime", TAG_Long
        ).value

    def _decode_biomes(self, chunk: Chunk, compound: TAG_Compound):
        biomes = compound.pop("Biomes")
        if isinstance(biomes, TAG_Byte_Array) and biomes.value.size == 256:
            chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))

    def _decode_height(self, chunk: Chunk, compound: TAG_Compound):
        height = self.get_obj(compound, "HeightMap", TAG_Int_Array).value
        if isinstance(height, numpy.ndarray) and height.size == 256:
            chunk.misc["height_map256IA"] = height.reshape((16, 16))

    def _extract_sections(
        self, chunk: Chunk, compound: TAG_Compound, key="Sections"
    ) -> Dict[int, TAG_Compound]:
        # parse sections into a more usable format
        sections: Dict[int, TAG_Compound] = {
            section.pop("Y").value: section
            for section in self.get_obj(compound, key, TAG_List)
            if isinstance(section, TAG_Compound)
            and self.check_type(section, "Y", TAG_Byte)
        }
        chunk.misc["java_sections"] = sections
        return sections

    def _decode_blocks(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ) -> AnyNDArray:
        raise NotImplementedError

    def _unpack_light(self, sections: Dict[int, TAG_Compound], section_key: str):
        light_container = {}
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
        return light_container

    def _decode_block_light(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ):
        chunk.misc["block_light"] = self._unpack_light(chunk_sections, "BlockLight")

    def _decode_sky_light(self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]):
        chunk.misc["sky_light"] = self._unpack_light(chunk_sections, "SkyLight")

    def _decode_entities(self, chunk: Chunk, compound: TAG_Compound, key="Entities"):
        ents = self._decode_entity_list(self.get_obj(compound, key, TAG_List))
        if amulet.entity_support:
            chunk.entities = ents
        else:
            chunk.misc["java_entities_temp"] = ents

    def _decode_entity_list(self, entities: TAG_List) -> List["Entity"]:
        entities_out = []
        if entities.list_data_type == TAG_Compound.tag_id:
            for nbt in entities:
                entity = self._decode_entity(
                    amulet_nbt.NBTFile(nbt),
                    self._features["entity_format"],
                    self._features["entity_coord_format"],
                )
                if entity is not None:
                    entities_out.append(entity)

        return entities_out

    def _decode_block_entities(
        self, chunk: Chunk, compound: TAG_Compound, key="TileEntities"
    ):
        chunk.block_entities = self._decode_block_entity_list(
            self.get_obj(compound, key, TAG_List)
        )

    def _decode_block_entity_list(
        self, block_entities: TAG_List
    ) -> List["BlockEntity"]:
        entities_out = []
        if block_entities.list_data_type == TAG_Compound.tag_id:
            for nbt in block_entities:
                if not isinstance(nbt, TAG_Compound):
                    continue
                entity = self._decode_block_entity(
                    amulet_nbt.NBTFile(nbt),
                    self._features["block_entity_format"],
                    self._features["block_entity_coord_format"],
                )
                if entity is not None:
                    entities_out.append(entity)

        return entities_out

    def _decode_block_ticks(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["tile_ticks"] = self.get_obj(compound, "TileTicks", TAG_List)

    def _decode_post_processing(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["post_processing"] = self.get_obj(
            compound, "PostProcessing", TAG_List
        )

    def _decode_structures(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["structures"] = self.get_obj(compound, "Structures", TAG_Compound)

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, int],
        bounds: Tuple[int, int],
    ) -> amulet_nbt.NBTFile:
        """
        Encode a version-specific chunk to raw data for the format to store.

        :param chunk: The already translated version-specfic chunk to encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :param bounds: The minimum and maximum bounds of the chunk. In 1.17 this is required to define where the biome array sits.
        :return: Raw data to be stored by the Format.
        """

        misc = chunk.misc
        if "java_chunk_data" in misc and isinstance(misc["java_chunk_data"], NBTFile):
            data = misc["java_chunk_data"]
        else:
            data = NBTFile()
        level: TAG_Compound = self.set_obj(data, "Level", TAG_Compound)
        level["xPos"] = TAG_Int(chunk.cx)
        level["zPos"] = TAG_Int(chunk.cz)
        if self._features["data_version"] == "int":
            data["DataVersion"] = amulet_nbt.TAG_Int(max_world_version[1])
        elif "DataVersion" in data:
            del data["DataVersion"]

        if self._features["last_update"] == "long":
            level["LastUpdate"] = amulet_nbt.TAG_Long(misc.get("last_update", 0))

        # Order the float value based on the order they would be run. Newer replacements for the same come just after
        # to save back find the next lowest valid value.
        if self._features["status"] in [StatusFormats.Java_13, StatusFormats.Java_14]:
            status = chunk.status.as_type(self._features["status"])
            level["Status"] = amulet_nbt.TAG_String(status)

        else:
            status = chunk.status.as_type(StatusFormats.Raw)
            if self._features["terrain_populated"] == "byte":
                level["TerrainPopulated"] = amulet_nbt.TAG_Byte(int(status > -0.3))

            if self._features["light_populated"] == "byte":
                level["LightPopulated"] = amulet_nbt.TAG_Byte(int(status > -0.2))

        if self._features["V"] == "byte":
            level["V"] = amulet_nbt.TAG_Byte(misc.get("V", 1))

        if self._features["inhabited_time"] == "long":
            level["InhabitedTime"] = amulet_nbt.TAG_Long(misc.get("inhabited_time", 0))

        if (
            self._features["biomes"] == BiomeState.BA256
        ):  # TODO: support the optional variant
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_2d()
                level["Biomes"] = amulet_nbt.TAG_Byte_Array(
                    chunk.biomes.astype(dtype=numpy.uint8)
                )
        elif self._features["biomes"] == BiomeState.IA256:
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_2d()
                level["Biomes"] = amulet_nbt.TAG_Int_Array(
                    chunk.biomes.astype(dtype=numpy.uint32)
                )
        elif self._features["biomes"] == BiomeState.IA1024:
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_3d()
                level["Biomes"] = amulet_nbt.TAG_Int_Array(
                    numpy.transpose(
                        numpy.asarray(chunk.biomes[:, 0:64, :]).astype(numpy.uint32),
                        (1, 2, 0),
                    ).ravel()  # YZX -> XYZ
                )
        elif self._features["biomes"] == BiomeState.IANx64:
            if chunk.status.value > -0.7:
                chunk.biomes.convert_to_3d()
                min_y, max_y = bounds
                level["Biomes"] = amulet_nbt.TAG_Int_Array(
                    numpy.transpose(
                        numpy.asarray(
                            chunk.biomes[:, min_y // 4 : max_y // 4, :]
                        ).astype(numpy.uint32),
                        (1, 2, 0),
                    ).ravel()  # YZX -> XYZ
                )

        if self._features["height_map"] in ["256IA", "256IARequired"]:
            height = misc.get("height_map256IA", None)
            if (
                isinstance(height, numpy.ndarray)
                and numpy.issubdtype(height.dtype, numpy.integer)
                and height.shape == (16, 16)
            ):
                level["HeightMap"] = amulet_nbt.TAG_Int_Array(height.ravel())
            elif self._features["height_map"] == "256IARequired":
                level["HeightMap"] = amulet_nbt.TAG_Int_Array(
                    numpy.zeros(256, dtype=numpy.uint32)
                )
        elif self._features["height_map"] in {"C|V1", "C|V2", "C|V3", "C|V4"}:
            maps = [
                "WORLD_SURFACE_WG",
                "OCEAN_FLOOR_WG",
                "MOTION_BLOCKING",
                "MOTION_BLOCKING_NO_LEAVES",
                "OCEAN_FLOOR",
            ]
            if self._features["height_map"] == "C|V1":  # 1466
                maps = ("LIQUID", "SOILD", "LIGHT", "RAIN")
            elif self._features["height_map"] == "C|V2":  # 1484
                maps.append("LIGHT_BLOCKING")
            elif self._features["height_map"] == "C|V3":  # 1503
                maps.append("LIGHT_BLOCKING")
                maps.append("WORLD_SURFACE")
            elif self._features["height_map"] == "C|V4":  # 1908
                maps.append("WORLD_SURFACE")
            else:
                raise Exception
            heightmaps_temp: Dict[str, numpy.ndarray] = misc.get("height_mapC", {})
            heightmaps = amulet_nbt.TAG_Compound()
            for heightmap in maps:
                if (
                    heightmap in heightmaps_temp
                    and isinstance(heightmaps_temp[heightmap], numpy.ndarray)
                    and heightmaps_temp[heightmap].size == 256
                ):
                    heightmaps[heightmap] = amulet_nbt.TAG_Long_Array(
                        encode_long_array(
                            heightmaps_temp[heightmap].ravel() - bounds[0],
                            (bounds[1] - bounds[0]).bit_length(),
                            self._features["long_array_format"] == "compact",
                        )
                    )
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

        if self._features["blocks"] in [
            "Sections|(Blocks,Data,Add)",
            "Sections|(BlockStates,Palette)",
        ]:
            cy_min, cy_max = bounds
            cy_min //= 16
            cy_max //= 16
            self._encode_blocks(sections, chunk.blocks, palette, cy_min, cy_max)
        else:
            raise Exception(f'Unsupported block format {self._features["blocks"]}')

        # these data versions probably extend a little into the snapshots as well
        if 1519 <= max_world_version[1] <= 1631:
            # Java 1.13 to 1.13.2 cannot have empty sections
            for cy in list(sections.keys()):
                if "BlockStates" not in sections[cy] or "Palette" not in sections[cy]:
                    del sections[cy]

        def pack_light(feature_key: str, section_key: str):
            if self._features[feature_key] == "Sections|2048BA":
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
                    elif self._features["light_optional"] == "false":
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

        if self._features["entities"] == "list":
            if amulet.entity_support:
                level["Entities"] = self._encode_entity_list(chunk.entities)
            else:
                level["Entities"] = self._encode_entity_list(
                    misc.get("java_entities_temp", amulet_nbt.TAG_List())
                )

        if self._features["block_entities"] == "list":
            level["TileEntities"] = self._encode_block_entity_list(chunk.block_entities)

        if self._features["tile_ticks"] in ["list", "list(optional)"]:
            ticks = misc.get("tile_ticks", amulet_nbt.TAG_List())
            if self._features["tile_ticks"] == "list(optional)":
                if len(ticks) > 0:
                    level["TileTicks"] = ticks
            elif self._features["tile_ticks"] == "list":
                level["TileTicks"] = ticks

        if self._features["liquid_ticks"] == "list":
            level["LiquidTicks"] = misc.get("liquid_ticks", amulet_nbt.TAG_List())

        if self._features["liquids_to_be_ticked"] == "16list|list":
            level["LiquidsToBeTicked"] = misc.get(
                "liquids_to_be_ticked",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self._features["to_be_ticked"] == "16list|list":
            level["ToBeTicked"] = misc.get(
                "to_be_ticked",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self._features["post_processing"] == "16list|list":
            level["PostProcessing"] = misc.get(
                "post_processing",
                amulet_nbt.TAG_List([amulet_nbt.TAG_List() for _ in range(16)]),
            )

        if self._features["structures"] == "compound":
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

    def _encode_entity_list(self, entities: Iterable["Entity"]) -> amulet_nbt.TAG_List:
        entities_out = []
        for entity in entities:
            nbt = self._encode_entity(
                entity,
                self._features["entity_format"],
                self._features["entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt.value)

        return amulet_nbt.TAG_List(entities_out)

    def _encode_block_entity_list(
        self, block_entities: Iterable["BlockEntity"]
    ) -> amulet_nbt.TAG_List:
        entities_out = []
        for entity in block_entities:
            nbt = self._encode_block_entity(
                entity,
                self._features["block_entity_format"],
                self._features["block_entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt.value)

        return amulet_nbt.TAG_List(entities_out)

    def _encode_blocks(
        self,
        sections: Dict[int, TAG_Compound],
        blocks: "Blocks",
        palette: AnyNDArray,
        cy_min: int,
        cy_max: int,
    ):
        raise NotImplementedError

from __future__ import annotations

from typing import Tuple, Dict, Sequence, Union, Type, TYPE_CHECKING

import numpy
from amulet_nbt import (
    TAG_Byte,
    TAG_Int,
    TAG_Long,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Byte_Array,
    TAG_Int_Array,
    BaseArrayType,
)

import amulet
from amulet.api.data_types import SubChunkNDArray, AnyNDArray, BlockCoordinates
from amulet.utils import world_utils
from amulet.api.wrapper import EntityIDType, EntityCoordType
from amulet.api.chunk import Chunk, StatusFormats, EntityList
from .base_anvil_interface import (
    BaseAnvilInterface,
    ChunkDataType,
    ChunkPathType,
)

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class AnvilNAInterface(BaseAnvilInterface):
    Level: ChunkPathType = ("region", [("Level", TAG_Compound)], TAG_Compound)
    Sections: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("Sections", TAG_List)],
        TAG_List,
    )

    BlockEntities: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("TileEntities", TAG_List)],
        TAG_List,
    )
    Entities: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("Entities", TAG_List)],
        TAG_List,
    )
    InhabitedTime: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("InhabitedTime", TAG_Long)],
        TAG_Long,
    )
    LastUpdate: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("LastUpdate", TAG_Long)],
        TAG_Compound,
    )
    HeightMap: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("HeightMap", TAG_Int_Array)],
        TAG_Int_Array,
    )
    TerrainPopulated: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("TerrainPopulated", TAG_Byte)],
        TAG_Byte,
    )
    LightPopulated: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("LightPopulated", TAG_Byte)],
        TAG_Byte,
    )
    V: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("V", TAG_Byte)],
        TAG_Byte(1),
    )
    BlockTicks: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("TileTicks", TAG_List)],
        TAG_List,
    )
    Biomes: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("Biomes", TAG_Byte_Array)],
        None,
    )

    def __init__(self):
        super().__init__()
        self._set_feature("height_map", "256IA")

        self._set_feature("light_optional", "false")

        self._set_feature("block_entity_format", EntityIDType.namespace_str_id)
        self._set_feature("block_entity_coord_format", EntityCoordType.xyz_int)

        self._set_feature("entity_format", EntityIDType.namespace_str_id)
        self._set_feature("entity_coord_format", EntityCoordType.Pos_list_double)

        self._register_decoder(self._decode_coords)
        self._register_decoder(self._decode_last_update)
        self._register_decoder(self._decode_status)
        self._register_decoder(self._decode_inhabited_time)
        self._register_decoder(self._decode_biomes)
        self._register_decoder(self._decode_height)
        self._register_decoder(self._decode_entities)
        self._register_decoder(self._decode_blocks)
        self._register_decoder(self._decode_block_entities)
        self._register_decoder(self._decode_block_ticks)
        self._register_decoder(self._decode_block_light)
        self._register_decoder(self._decode_sky_light)

        self._register_decoder(self._post_decode_sections)

    @staticmethod
    def minor_is_valid(key: int):
        return key == -1

    def decode(
        self, cx: int, cz: int, data: ChunkDataType, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        chunk = self._init_decode(cx, cz, data)
        cy_min = self._get_floor_cy(data)
        cy_max = bounds[1] >> 4
        self._do_decode(chunk, data, cy_min, cy_max)
        block_array = chunk.misc.pop("block_array")
        return chunk, block_array

    def _get_floor_cy(self, data: ChunkDataType):
        return 0

    @staticmethod
    def _init_decode(cx: int, cz: int, data: ChunkDataType) -> Chunk:
        """Get the decode started by creating a chunk object."""
        chunk = Chunk(cx, cz)
        chunk.misc = {
            # store the chunk data so that any non-versioned data can get saved back
            "_java_chunk_data_layers": data
        }
        # TODO: move this into the entity section
        # if amulet.experimental_entity_support and "entities" in data:
        #     # TODO: handle this better
        #     chunk._native_entities = EntityList(data["entities"]["Entities"])
        #     chunk._native_version = data["entities"]["DataVersion"].value
        return chunk

    def _get_level(self, data: ChunkDataType) -> TAG_Compound:
        """
        Get the level data container
        For older levels this is region:Level but newer worlds it is in region root
        :param data: The raw chunk data
        :return: The level data compound
        """
        return self.get_layer_obj(data, self.Level)

    def _decode_coords(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        level = self._get_level(data)
        assert chunk.coordinates == (level.pop("xPos"), level.pop("zPos"))

    def _decode_last_update(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        chunk.misc["last_update"] = self.get_layer_obj(
            data, self.LastUpdate, pop_last=True
        ).value

    def _decode_status(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        status = "empty"
        if self.get_layer_obj(data, self.TerrainPopulated, pop_last=True):
            status = "decorated"
        if self.get_layer_obj(data, self.LightPopulated, pop_last=True):
            status = "postprocessed"
        chunk.status = status

    def _decode_v_tag(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        chunk.misc["V"] = self.get_layer_obj(data, self.V, pop_last=True).value

    def _decode_inhabited_time(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        chunk.misc["inhabited_time"] = self.get_layer_obj(
            data, self.InhabitedTime, pop_last=True
        ).value

    def _decode_biomes(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        biomes = self.get_layer_obj(data, self.Biomes, pop_last=True)
        if isinstance(biomes, BaseArrayType) and biomes.value.size == 256:
            chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))

    def _decode_height(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        height = self.get_layer_obj(data, self.HeightMap, pop_last=True).value
        if isinstance(height, numpy.ndarray) and height.size == 256:
            chunk.misc["height_map256IA"] = height.reshape((16, 16))

    def _iter_sections(self, data: ChunkDataType):
        sections: TAG_List = self.get_layer_obj(data, self.Sections)
        for section in sections:
            yield section["Y"].value, section

    def _post_decode_sections(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        sections = self.get_layer_obj(data, self.Sections)
        if sections:
            for i in range(len(sections) - 1, -1, -1):
                section = sections[i]
                if section.keys() == {"Y"}:
                    # if only the Y key exists we can remove it
                    sections.pop(i)
        if not sections:
            # if no sections remain we can remove the sections data
            self.get_layer_obj(data, self.Sections, pop_last=True)

    def _decode_blocks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        blocks: Dict[int, SubChunkNDArray] = {}
        palette = []
        palette_len = 0
        for cy, section in self._iter_sections(data):
            section_blocks = numpy.frombuffer(
                section.pop("Blocks").value, dtype=numpy.uint8
            )
            section_data = numpy.frombuffer(
                section.pop("Data").value, dtype=numpy.uint8
            )
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks = section_blocks.astype(numpy.uint16)

            section_data = world_utils.from_nibble_array(section_data)
            section_data = section_data.reshape((16, 16, 16))

            if "Add" in section:
                add_blocks = numpy.frombuffer(
                    section.pop("Add").value, dtype=numpy.uint8
                )
                add_blocks = world_utils.from_nibble_array(add_blocks)
                add_blocks = add_blocks.reshape((16, 16, 16))

                section_blocks |= add_blocks.astype(numpy.uint16) << 8
                # TODO: fix this

            (section_palette, blocks[cy]) = world_utils.fast_unique(
                numpy.transpose(
                    (section_blocks << 4) + section_data, (2, 0, 1)
                )  # YZX -> XYZ
            )
            blocks[cy] += palette_len
            palette_len += len(section_palette)
            palette.append(section_palette)

        if palette:
            final_palette, lut = numpy.unique(
                numpy.concatenate(palette), return_inverse=True
            )
            final_palette: numpy.ndarray = numpy.array(
                [final_palette >> 4, final_palette & 15]
            ).T
            for cy in blocks:
                blocks[cy] = lut[blocks[cy]]
        else:
            final_palette = numpy.array([], dtype=object)
        chunk.blocks = blocks
        chunk.misc["block_array"] = final_palette

    def _unpack_light(
        self, data: ChunkDataType, section_key: str
    ) -> Dict[int, numpy.ndarray]:
        light_container = {}
        for cy, section in self._iter_sections(data):
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
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        chunk.misc["block_light"] = self._unpack_light(data, "BlockLight")

    def _decode_sky_light(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        chunk.misc["sky_light"] = self._unpack_light(data, "SkyLight")

    def _decode_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        ents = self._decode_entity_list(
            self.get_layer_obj(data, self.Entities, pop_last=True)
        )
        if amulet.entity_support:
            chunk.entities = ents
        elif amulet.experimental_entity_support:
            chunk._native_entities.extend(ents)
        else:
            chunk.misc["java_entities_temp"] = ents

    def _decode_block_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        chunk.block_entities = self._decode_block_entity_list(
            self.get_layer_obj(data, self.BlockEntities, pop_last=True)
        )

    @staticmethod
    def _decode_ticks(ticks: TAG_List) -> Dict[BlockCoordinates, Tuple[str, int, int]]:
        return {
            (tick["x"].value, tick["y"].value, tick["z"].value): (
                tick["i"].value,
                tick["t"].value,
                tick["p"].value,
            )
            for tick in ticks
            if all(c in tick and isinstance(tick[c], TAG_Int) for c in "xyztp")
            and "i" in tick
            and isinstance(tick["i"], TAG_String)
        }

    def _decode_block_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, ceil_cy: int
    ):
        chunk.misc.setdefault("block_ticks", {}).update(
            self._decode_ticks(self.get_layer_obj(data, self.BlockTicks, pop_last=True))
        )

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, int],
        bounds: Tuple[int, int],
    ) -> ChunkDataType:
        raise NotImplementedError

    #     root = self._init_encode(chunk)
    #     self._encode_root(root, max_world_version)
    #     level: TAG_Compound = self.set_obj(root["region"], "Level", TAG_Compound)
    #     self._encode_level(chunk, level, bounds)
    #     sections = self._init_sections(chunk)
    #     self._encode_sections(chunk, sections, bounds)
    #     self._encode_blocks(chunk, sections, palette, bounds)
    #     # these data versions probably extend a little into the snapshots as well
    #     if 1519 <= max_world_version[1] <= 1631:
    #         # Java 1.13 to 1.13.2 cannot have empty sections
    #         for cy in list(sections.keys()):
    #             if "BlockStates" not in sections[cy] or "Palette" not in sections[cy]:
    #                 del sections[cy]
    #     sections_list = []
    #     for cy, section in sections.items():
    #         section["Y"] = TAG_Byte(cy)
    #         sections_list.append(section)
    #     level[self.Sections] = TAG_List(sections_list)
    #     return {k: NBTFile(v) for k, v in root.items()}
    #
    # @staticmethod
    # def _init_encode(chunk: "Chunk") -> Dict[str, TAG_Compound]:
    #     """Get or create the root tag."""
    #     if "java_chunk_data" in chunk.misc and isinstance(
    #         chunk.misc["java_chunk_data"], TAG_Compound
    #     ):
    #         return {"region": chunk.misc["java_chunk_data"]}
    #     else:
    #         return {"region": TAG_Compound()}
    #
    # def _encode_root(self, root: TAG_Compound, max_world_version: Tuple[str, int]):
    #     self._encode_data_version(root, max_world_version)
    #
    # def _encode_data_version(
    #     self, root: TAG_Compound, max_world_version: Tuple[str, int]
    # ):
    #     if "DataVersion" in root:
    #         del root["DataVersion"]
    #
    # def _encode_level(self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]):
    #     self._encode_coords(chunk, level, bounds)
    #     self._encode_last_update(chunk, level)
    #     self._encode_status(chunk, level)
    #     self._encode_inhabited_time(chunk, level)
    #     self._encode_biomes(chunk, level, bounds)
    #     self._encode_height(chunk, level, bounds)
    #     self._encode_entities(chunk, level)
    #     self._encode_block_entities(chunk, level)
    #     self._encode_block_ticks(chunk, level, bounds)
    #
    # @staticmethod
    # def _init_sections(chunk: "Chunk") -> Dict[int, TAG_Compound]:
    #     """Get or create the root tag."""
    #     if "java_sections" in chunk.misc and isinstance(
    #         chunk.misc["java_sections"], dict
    #     ):
    #         # verify that the data is correctly formatted.
    #         return {
    #             cy: section
    #             for cy, section in chunk.misc["java_sections"].items()
    #             if isinstance(cy, int) and isinstance(section, TAG_Compound)
    #         }
    #     else:
    #         return {}
    #
    # def _encode_block_section(
    #     self,
    #     chunk: Chunk,
    #     sections: Dict[int, TAG_Compound],
    #     palette: AnyNDArray,
    #     cy: int,
    # ) -> bool:
    #     if cy in chunk.blocks:
    #         block_sub_array = palette[
    #             numpy.transpose(
    #                 chunk.blocks.get_sub_chunk(cy), (1, 2, 0)
    #             ).ravel()  # XYZ -> YZX
    #         ]
    #
    #         data_sub_array = block_sub_array[:, 1]
    #         block_sub_array = block_sub_array[:, 0]
    #         # if not numpy.any(block_sub_array) and not numpy.any(data_sub_array):
    #         #     return False
    #         section = sections.setdefault(cy, TAG_Compound())
    #         section["Blocks"] = TAG_Byte_Array(block_sub_array.astype("uint8"))
    #         section["Data"] = TAG_Byte_Array(
    #             world_utils.to_nibble_array(data_sub_array)
    #         )
    #         return True
    #     return False
    #
    # def _encode_blocks(
    #     self,
    #     chunk: Chunk,
    #     sections: Dict[int, TAG_Compound],
    #     palette: AnyNDArray,
    #     bounds: Tuple[int, int],
    # ):
    #     for cy in range(bounds[0] >> 4, bounds[1] >> 4):
    #         if not self._encode_block_section(chunk, sections, palette, cy):
    #             # In 1.13.2 and before if the Blocks key does not exist but the sub-chunk TAG_Compound does
    #             # exist the game will error and recreate the chunk. All sub-chunks that do not contain data
    #             # must be deleted.
    #             if cy in sections:
    #                 del sections[cy]
    #
    # @staticmethod
    # def _encode_coords(chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]):
    #     level["xPos"] = TAG_Int(chunk.cx)
    #     level["zPos"] = TAG_Int(chunk.cz)
    #
    # @staticmethod
    # def _encode_last_update(chunk: Chunk, level: TAG_Compound):
    #     level["LastUpdate"] = TAG_Long(chunk.misc.get("last_update", 0))
    #
    # def _encode_status(self, chunk: Chunk, level: TAG_Compound):
    #     status = chunk.status.as_type(StatusFormats.Raw)
    #     level["TerrainPopulated"] = TAG_Byte(int(status > -0.3))
    #     level["LightPopulated"] = TAG_Byte(int(status > -0.2))
    #
    # @staticmethod
    # def _encode_v_tag(chunk: Chunk, level: TAG_Compound):
    #     level["V"] = TAG_Byte(chunk.misc.get("V", 1))
    #
    # def _encode_inhabited_time(self, chunk: Chunk, level: TAG_Compound):
    #     level["InhabitedTime"] = TAG_Long(chunk.misc.get("inhabited_time", 0))
    #
    # def _encode_biomes(
    #     self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    # ):
    #     chunk.biomes.convert_to_2d()
    #     level["Biomes"] = TAG_Byte_Array(chunk.biomes.astype(dtype=numpy.uint8).ravel())
    #
    # def _encode_height(
    #     self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    # ):
    #     height = chunk.misc.get("height_map256IA", None)
    #     if (
    #         isinstance(height, numpy.ndarray)
    #         and numpy.issubdtype(height.dtype, numpy.integer)
    #         and height.shape == (16, 16)
    #     ):
    #         level["HeightMap"] = TAG_Int_Array(height.ravel())
    #     elif self._features["height_map"] == "256IARequired":
    #         level["HeightMap"] = TAG_Int_Array(numpy.zeros(256, dtype=numpy.uint32))
    #
    # def _encode_entities(self, chunk: Chunk, level: TAG_Compound):
    #     if amulet.entity_support:
    #         level[self.Entities] = self._encode_entity_list(chunk.entities)
    #     elif amulet.experimental_entity_support:
    #         level[self.Entities] = self._encode_entity_list(chunk._native_entities)
    #     else:
    #         level[self.Entities] = self._encode_entity_list(
    #             chunk.misc.get("java_entities_temp", TAG_List())
    #         )
    #
    # def _encode_block_entities(self, chunk: Chunk, level: TAG_Compound):
    #     level[self.BlockEntities] = self._encode_block_entity_list(chunk.block_entities)
    #
    # @staticmethod
    # def _encode_ticks(ticks: Dict[BlockCoordinates, Tuple[str, int, int]]) -> TAG_List:
    #     ticks_out = TAG_List()
    #     if isinstance(ticks, dict):
    #         for k, v in ticks.items():
    #             try:
    #                 (x, y, z), (i, t, p) = k, v
    #                 ticks_out.append(
    #                     TAG_Compound(
    #                         {
    #                             "i": TAG_String(i),
    #                             "p": TAG_Int(p),
    #                             "t": TAG_Int(t),
    #                             "x": TAG_Int(x),
    #                             "y": TAG_Int(y),
    #                             "z": TAG_Int(x),
    #                         }
    #                     )
    #                 )
    #             except Exception:
    #                 amulet.log.error(f"Could not serialise tick data {k}: {v}")
    #     return ticks_out
    #
    # def _encode_block_ticks(
    #     self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    # ):
    #     level["TileTicks"] = self._encode_ticks(chunk.misc.get("block_ticks", {}))
    #
    # def _encode_sections(
    #     self, chunk: Chunk, sections: Dict[int, TAG_Compound], bounds: Tuple[int, int]
    # ):
    #     self._encode_block_light(chunk, sections)
    #     self._encode_sky_light(chunk, sections)
    #
    # def _pack_light(
    #     self,
    #     chunk: Chunk,
    #     sections: Dict[int, TAG_Compound],
    #     feature_key: str,
    #     section_key: str,
    # ):
    #     light_container = chunk.misc.get(feature_key, {})
    #     if not isinstance(light_container, dict):
    #         light_container = {}
    #     for cy, section in sections.items():
    #         light = light_container.get(cy, None)
    #         if (
    #             isinstance(light, numpy.ndarray)
    #             and numpy.issubdtype(light.dtype, numpy.integer)
    #             and light.shape == (16, 16, 16)
    #         ):
    #             light = light.ravel() % 16
    #             section[section_key] = TAG_Byte_Array(light[::2] + (light[1::2] << 4))
    #         elif self._features["light_optional"] == "false":
    #             section[section_key] = TAG_Byte_Array(
    #                 numpy.full(2048, 255, dtype=numpy.uint8)
    #             )
    #
    # def _encode_block_light(self, chunk: Chunk, sections: Dict[int, TAG_Compound]):
    #     self._pack_light(chunk, sections, "block_light", "BlockLight")
    #
    # def _encode_sky_light(self, chunk: Chunk, sections: Dict[int, TAG_Compound]):
    #     self._pack_light(chunk, sections, "sky_light", "SkyLight")


export = AnvilNAInterface

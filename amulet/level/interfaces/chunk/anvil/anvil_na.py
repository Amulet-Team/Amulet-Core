from __future__ import annotations

from typing import Tuple, Dict, List, TYPE_CHECKING

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
    NBTFile,
)

import amulet
from amulet.api.data_types import SubChunkNDArray, AnyNDArray, BlockCoordinates
from amulet.utils import world_utils
from amulet.api.wrapper import EntityIDType, EntityCoordType
from amulet.api.chunk import Chunk, StatusFormats, EntityList
from amulet.api.entity import Entity
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
    xPos: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("xPos", TAG_Int)],
        TAG_Int,
    )
    zPos: ChunkPathType = (
        "region",
        [("Level", TAG_Compound), ("zPos", TAG_Int)],
        TAG_Int,
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
        self._register_decoder(self._decode_v_tag)
        self._register_decoder(self._decode_inhabited_time)
        self._register_decoder(self._decode_biomes)
        self._register_decoder(self._decode_height)
        self._register_decoder(self._decode_entities)
        self._register_decoder(self._decode_blocks)
        self._register_decoder(self._decode_block_entities)
        self._register_decoder(self._decode_block_ticks)
        self._register_decoder(self._decode_block_light)
        self._register_decoder(self._decode_sky_light)

        self._register_post_decoder(self._post_decode_sections)

        self._register_encoder(self._encode_coords)
        self._register_encoder(self._encode_last_update)
        self._register_encoder(self._encode_status)
        self._register_encoder(self._encode_v_tag)
        self._register_encoder(self._encode_inhabited_time)
        self._register_encoder(self._encode_biomes)
        self._register_encoder(self._encode_height)
        self._register_encoder(self._encode_entities)
        self._register_encoder(self._encode_blocks)
        self._register_encoder(self._encode_block_entities)
        self._register_encoder(self._encode_block_ticks)
        self._register_encoder(self._encode_block_light)
        self._register_encoder(self._encode_sky_light)

    @staticmethod
    def minor_is_valid(key: int):
        return key == -1

    def decode(
        self, cx: int, cz: int, data: ChunkDataType, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        chunk = self._init_decode(cx, cz, data)
        floor_cy = self._get_floor_cy(data)
        height_cy = (bounds[1] - bounds[0]) >> 4
        self._do_decode(chunk, data, floor_cy, height_cy)
        block_palette = chunk.misc.pop("block_palette")
        return chunk, block_palette

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
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.get_layer_obj(data, self.xPos, pop_last=True)
        self.get_layer_obj(data, self.zPos, pop_last=True)

    def _decode_last_update(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["last_update"] = self.get_layer_obj(
            data, self.LastUpdate, pop_last=True
        ).value

    def _decode_status(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        status = "empty"
        if self.get_layer_obj(data, self.TerrainPopulated, pop_last=True):
            status = "decorated"
        if self.get_layer_obj(data, self.LightPopulated, pop_last=True):
            status = "postprocessed"
        chunk.status = status

    def _decode_v_tag(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["V"] = self.get_layer_obj(data, self.V, pop_last=True).value

    def _decode_inhabited_time(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["inhabited_time"] = self.get_layer_obj(
            data, self.InhabitedTime, pop_last=True
        ).value

    def _decode_biomes(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        biomes = self.get_layer_obj(data, self.Biomes, pop_last=True)
        if isinstance(biomes, BaseArrayType) and biomes.value.size == 256:
            chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))

    def _decode_height(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        height = self.get_layer_obj(data, self.HeightMap, pop_last=True).value
        if isinstance(height, numpy.ndarray) and height.size == 256:
            chunk.misc["height_map256IA"] = height.reshape((16, 16))

    def _iter_sections(self, data: ChunkDataType):
        sections: TAG_List = self.get_layer_obj(data, self.Sections)
        for section in sections:
            yield section["Y"].value, section

    def _post_decode_sections(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        """Strip out all empty sections"""
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
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        blocks: Dict[int, SubChunkNDArray] = {}
        palette = []
        palette_len = 0
        for cy, section in self._iter_sections(data):
            block_tag = section.pop("Blocks", None)
            data_tag = section.pop("Data", None)
            if not isinstance(block_tag, BaseArrayType) or not isinstance(
                data_tag, BaseArrayType
            ):
                continue
            section_blocks = numpy.frombuffer(block_tag.value, dtype=numpy.uint8)
            section_data = numpy.frombuffer(data_tag.value, dtype=numpy.uint8)
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks = section_blocks.astype(numpy.uint16)

            section_data = world_utils.from_nibble_array(section_data)
            section_data = section_data.reshape((16, 16, 16))

            add_tag = section.pop("Add", None)
            if isinstance(add_tag, BaseArrayType):
                add_blocks = numpy.frombuffer(add_tag.value, dtype=numpy.uint8)
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
        chunk.misc["block_palette"] = final_palette

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
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["block_light"] = self._unpack_light(data, "BlockLight")

    def _decode_sky_light(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["sky_light"] = self._unpack_light(data, "SkyLight")

    def _decode_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        ents = self._decode_entity_list(
            self.get_layer_obj(data, self.Entities, pop_last=True)
        )
        if amulet.entity_support:
            chunk.entities = ents
        else:
            chunk._native_entities.extend(ents)
            chunk._native_version = ("java", -1)

    def _decode_block_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
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
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
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
        floor_cy = bounds[0] >> 4
        height_cy = (bounds[1] - bounds[0]) >> 4
        data = self._init_encode(chunk, max_world_version, floor_cy, height_cy)
        chunk.misc["block_palette"] = palette
        self._do_encode(chunk, data, floor_cy, height_cy)
        return data

    def _init_encode(
        self,
        chunk: "Chunk",
        max_world_version: Tuple[str, int],
        floor_cy: int,
        height_cy: int,
    ) -> ChunkDataType:
        """Get or create the root data."""
        data = chunk.misc.get("_java_chunk_data_layers", None)
        if not isinstance(data, dict):
            data = {}
        return {
            key: value
            for key, value in data.items()
            if isinstance(key, str) and isinstance(value, NBTFile)
        }

    def _get_encode_sections(
        self,
        data: ChunkDataType,
        floor_cy: int,
        height_cy: int,
    ) -> Dict[int, TAG_Compound]:
        """Get or create the section array populating all valid sections"""
        sections = self.set_layer_obj(data, self.Sections, setdefault=True)
        section_map: Dict[int, TAG_Compound] = {}
        for section_index in range(len(sections) - 1, -1, -1):
            section = sections[section_index]
            cy = section.get("Y", None)
            if isinstance(cy, TAG_Byte):
                section_map[cy.value] = section
            else:
                sections.pop(section_index)
        for cy in range(floor_cy, floor_cy + height_cy):
            if cy not in section_map:
                section = section_map[cy] = TAG_Compound({"Y": TAG_Byte(cy)})
                sections.append(section)
        return section_map

    def _encode_block_section(
        self,
        chunk: Chunk,
        sections: Dict[int, TAG_Compound],
        palette: AnyNDArray,
        cy: int,
    ):
        block_sub_array = palette[
            numpy.transpose(
                chunk.blocks.get_sub_chunk(cy), (1, 2, 0)
            ).ravel()  # XYZ -> YZX
        ]

        data_sub_array = block_sub_array[:, 1]
        block_sub_array = block_sub_array[:, 0]
        # if not numpy.any(block_sub_array) and not numpy.any(data_sub_array):
        #     return False
        sections[cy]["Blocks"] = TAG_Byte_Array(block_sub_array.astype("uint8"))
        sections[cy]["Data"] = TAG_Byte_Array(
            world_utils.to_nibble_array(data_sub_array)
        )

    def _encode_blocks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        sections = self._get_encode_sections(data, floor_cy, height_cy)
        block_palette = chunk.misc.pop("block_palette")
        ceil_cy = floor_cy + height_cy
        for cy in chunk.blocks.sub_chunks:
            if floor_cy <= cy < ceil_cy:
                self._encode_block_section(chunk, sections, block_palette, cy)

    def _encode_coords(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(data, self.xPos, TAG_Int(chunk.cx))
        self.set_layer_obj(data, self.zPos, TAG_Int(chunk.cz))

    def _encode_last_update(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data, self.LastUpdate, TAG_Long(chunk.misc.get("last_update", 0))
        )

    def _encode_status(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        status = chunk.status.as_type(StatusFormats.Raw)
        self.set_layer_obj(data, self.TerrainPopulated, TAG_Byte(int(status > -0.3)))
        self.set_layer_obj(data, self.LightPopulated, TAG_Byte(int(status > -0.2)))

    def _encode_v_tag(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(data, self.V, TAG_Byte(chunk.misc.get("V", 1)))

    def _encode_inhabited_time(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data, self.InhabitedTime, TAG_Long(chunk.misc.get("inhabited_time", 0))
        )

    def _encode_biomes(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.biomes.convert_to_2d()
        self.set_layer_obj(
            data,
            self.Biomes,
            TAG_Byte_Array(chunk.biomes.astype(dtype=numpy.uint8).ravel()),
        )

    def _encode_height(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        height = chunk.misc.get("height_map256IA", None)
        if (
            isinstance(height, numpy.ndarray)
            and numpy.issubdtype(height.dtype, numpy.integer)
            and height.shape == (16, 16)
        ):
            self.set_layer_obj(
                data,
                self.HeightMap,
                TAG_Int_Array(numpy.zeros(256, dtype=numpy.uint32)),
            )
        elif self._features["height_map"] == "256IARequired":
            self.set_layer_obj(data, self.HeightMap, TAG_Int_Array(height.ravel()))

    def _encode_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        if amulet.entity_support:
            entities = chunk.entities
        else:
            entities = chunk._native_entities

        self.set_layer_obj(
            data,
            self.Entities,
            self._encode_entity_list(entities),
        )

    def _encode_block_entities(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data,
            self.BlockEntities,
            self._encode_block_entity_list(chunk.block_entities),
        )

    @staticmethod
    def _encode_ticks(ticks: Dict[BlockCoordinates, Tuple[str, int, int]]) -> TAG_List:
        ticks_out = TAG_List()
        if isinstance(ticks, dict):
            for k, v in ticks.items():
                try:
                    (x, y, z), (i, t, p) = k, v
                    ticks_out.append(
                        TAG_Compound(
                            {
                                "i": TAG_String(i),
                                "p": TAG_Int(p),
                                "t": TAG_Int(t),
                                "x": TAG_Int(x),
                                "y": TAG_Int(y),
                                "z": TAG_Int(x),
                            }
                        )
                    )
                except Exception:
                    amulet.log.error(f"Could not serialise tick data {k}: {v}")
        return ticks_out

    def _encode_block_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data, self.BlockTicks, self._encode_ticks(chunk.misc.get("block_ticks", {}))
        )

    def _pack_light(
        self,
        chunk: Chunk,
        data: ChunkDataType,
        floor_cy: int,
        height_cy: int,
        feature_key: str,
        section_key: str,
    ):
        light_container = chunk.misc.get(feature_key, {})
        if not isinstance(light_container, dict):
            light_container = {}
        for cy, section in self._get_encode_sections(data, floor_cy, height_cy).items():
            light = light_container.get(cy, None)
            if (
                isinstance(light, numpy.ndarray)
                and numpy.issubdtype(light.dtype, numpy.integer)
                and light.shape == (16, 16, 16)
            ):
                light = light.ravel() % 16
                section[section_key] = TAG_Byte_Array(light[::2] + (light[1::2] << 4))
            elif self._features["light_optional"] == "false":
                section[section_key] = TAG_Byte_Array(
                    numpy.full(2048, 255, dtype=numpy.uint8)
                )

    def _encode_block_light(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self._pack_light(chunk, data, floor_cy, height_cy, "block_light", "BlockLight")

    def _encode_sky_light(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self._pack_light(chunk, data, floor_cy, height_cy, "sky_light", "SkyLight")


export = AnvilNAInterface

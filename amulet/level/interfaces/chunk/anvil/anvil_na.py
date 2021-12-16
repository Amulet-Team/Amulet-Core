from __future__ import annotations

from typing import Tuple, Dict, TYPE_CHECKING

import numpy
from amulet_nbt import (
    NBTFile,
    TAG_Byte,
    TAG_Int,
    TAG_Long,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Byte_Array,
    TAG_Int_Array,
)

import amulet
from amulet.api.data_types import SubChunkNDArray, AnyNDArray, BlockCoordinates
from amulet.utils import world_utils
from amulet.api.wrapper import EntityIDType, EntityCoordType
from amulet.api.chunk import Chunk, StatusFormats
from .base_anvil_interface import (
    BaseAnvilInterface,
)

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class AnvilNAInterface(BaseAnvilInterface):
    BlockEntities = "TileEntities"
    Entities = "Entities"
    Sections = "Sections"

    def __init__(self):
        super().__init__()
        self._set_feature("height_map", "256IA")

        self._set_feature("light_optional", "false")

        self._set_feature("block_entity_format", EntityIDType.namespace_str_id)
        self._set_feature("block_entity_coord_format", EntityCoordType.xyz_int)

        self._set_feature("entity_format", EntityIDType.namespace_str_id)
        self._set_feature("entity_coord_format", EntityCoordType.Pos_list_double)

    @staticmethod
    def minor_is_valid(key: int):
        return key == -1

    def decode(
        self, cx: int, cz: int, nbt_file: NBTFile, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        chunk, root = self._init_decode(cx, cz, nbt_file)
        return self._decode_chunk(chunk, root, bounds)

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

    def _decode_chunk(
        self, chunk: Chunk, root: TAG_Compound, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        self._decode_root(chunk, root)
        assert self.check_type(root, "Level", TAG_Compound)
        level = root.pop("Level")
        self._decode_level(chunk, level, bounds, bounds[0] >> 4)
        sections = self._extract_sections(chunk, level)
        self._decode_sections(chunk, sections)
        palette = self._decode_blocks(chunk, sections)
        return chunk, palette

    def _decode_root(self, chunk: Chunk, root: TAG_Compound):
        pass

    def _decode_level(
        self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int], floor_cy: int
    ):
        self._decode_coords(chunk, level)
        self._decode_last_update(chunk, level)
        self._decode_status(chunk, level)
        self._decode_inhabited_time(chunk, level)
        self._decode_biomes(chunk, level, floor_cy)
        self._decode_height(chunk, level, bounds)
        self._decode_entities(chunk, level)
        self._decode_block_entities(chunk, level)
        self._decode_block_ticks(chunk, level, floor_cy)

    def _decode_sections(self, chunk: Chunk, sections: Dict[int, TAG_Compound]):
        self._decode_block_light(chunk, sections)
        self._decode_sky_light(chunk, sections)

    @staticmethod
    def _decode_coords(chunk: Chunk, level: TAG_Compound):
        assert chunk.coordinates == (level.pop("xPos"), level.pop("zPos"))

    def _decode_last_update(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["last_update"] = self.get_obj(compound, "LastUpdate", TAG_Long).value

    def _decode_status(self, chunk: Chunk, compound: TAG_Compound):
        status = "empty"
        if self.get_obj(compound, "TerrainPopulated", TAG_Byte):
            status = "decorated"
        if self.get_obj(compound, "LightPopulated", TAG_Byte):
            status = "postprocessed"
        chunk.status = status

    def _decode_v_tag(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["V"] = self.get_obj(compound, "V", TAG_Byte, TAG_Byte(1)).value

    def _decode_inhabited_time(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["inhabited_time"] = self.get_obj(
            compound, "InhabitedTime", TAG_Long
        ).value

    def _decode_biomes(self, chunk: Chunk, compound: TAG_Compound, floor_cy: int):
        biomes = compound.pop("Biomes", None)
        if isinstance(biomes, TAG_Byte_Array) and biomes.value.size == 256:
            chunk.biomes = biomes.astype(numpy.uint32).reshape((16, 16))

    def _decode_height(
        self, chunk: Chunk, compound: TAG_Compound, bounds: Tuple[int, int]
    ):
        height = self.get_obj(compound, "HeightMap", TAG_Int_Array).value
        if isinstance(height, numpy.ndarray) and height.size == 256:
            chunk.misc["height_map256IA"] = height.reshape((16, 16))

    def _extract_sections(
        self, chunk: Chunk, compound: TAG_Compound
    ) -> Dict[int, TAG_Compound]:
        # parse sections into a more usable format
        sections: Dict[int, TAG_Compound] = {
            section.pop("Y").value: section
            for section in self.get_obj(compound, self.Sections, TAG_List)
            if isinstance(section, TAG_Compound)
            and self.check_type(section, "Y", TAG_Byte)
        }
        chunk.misc["java_sections"] = sections
        return sections

    def _decode_blocks(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ) -> AnyNDArray:
        blocks: Dict[int, SubChunkNDArray] = {}
        palette = []
        palette_len = 0
        for cy, section in chunk_sections.items():
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
        return final_palette

    def _unpack_light(
        self, sections: Dict[int, TAG_Compound], section_key: str
    ) -> Dict[int, numpy.ndarray]:
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

    def _decode_entities(self, chunk: Chunk, compound: TAG_Compound):
        ents = self._decode_entity_list(self.get_obj(compound, self.Entities, TAG_List))
        if amulet.entity_support:
            chunk.entities = ents
        else:
            chunk.misc["java_entities_temp"] = ents

    def _decode_block_entities(self, chunk: Chunk, compound: TAG_Compound):
        chunk.block_entities = self._decode_block_entity_list(
            self.get_obj(compound, self.BlockEntities, TAG_List)
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

    def _decode_block_ticks(self, chunk: Chunk, compound: TAG_Compound, floor_cy: int):
        chunk.misc.setdefault("block_ticks", {}).update(
            self._decode_ticks(self.get_obj(compound, "TileTicks", TAG_List))
        )

    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, int],
        bounds: Tuple[int, int],
    ) -> NBTFile:
        return NBTFile(self._encode_chunk(chunk, palette, max_world_version, bounds))

    def _encode_chunk(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, int],
        bounds: Tuple[int, int],
    ) -> TAG_Compound:
        root = self._init_encode(chunk)
        self._encode_root(root, max_world_version)
        level: TAG_Compound = self.set_obj(root, "Level", TAG_Compound)
        self._encode_level(chunk, level, bounds)
        sections = self._init_sections(chunk)
        self._encode_sections(chunk, sections, bounds)
        self._encode_blocks(chunk, sections, palette, bounds)
        # these data versions probably extend a little into the snapshots as well
        if 1519 <= max_world_version[1] <= 1631:
            # Java 1.13 to 1.13.2 cannot have empty sections
            for cy in list(sections.keys()):
                if "BlockStates" not in sections[cy] or "Palette" not in sections[cy]:
                    del sections[cy]
        sections_list = []
        for cy, section in sections.items():
            section["Y"] = TAG_Byte(cy)
            sections_list.append(section)
        level[self.Sections] = TAG_List(sections_list)
        return root

    @staticmethod
    def _init_encode(chunk: "Chunk"):
        """Get or create the root tag."""
        if "java_chunk_data" in chunk.misc and isinstance(
            chunk.misc["java_chunk_data"], TAG_Compound
        ):
            return chunk.misc["java_chunk_data"]
        else:
            return TAG_Compound()

    def _encode_root(self, root: TAG_Compound, max_world_version: Tuple[str, int]):
        self._encode_data_version(root, max_world_version)

    def _encode_data_version(
        self, root: TAG_Compound, max_world_version: Tuple[str, int]
    ):
        if "DataVersion" in root:
            del root["DataVersion"]

    def _encode_level(self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]):
        self._encode_coords(chunk, level, bounds)
        self._encode_last_update(chunk, level)
        self._encode_status(chunk, level)
        self._encode_inhabited_time(chunk, level)
        self._encode_biomes(chunk, level, bounds)
        self._encode_height(chunk, level, bounds)
        self._encode_entities(chunk, level)
        self._encode_block_entities(chunk, level)
        self._encode_block_ticks(chunk, level, bounds)

    @staticmethod
    def _init_sections(chunk: "Chunk") -> Dict[int, TAG_Compound]:
        """Get or create the root tag."""
        if "java_sections" in chunk.misc and isinstance(
            chunk.misc["java_sections"], dict
        ):
            # verify that the data is correctly formatted.
            return {
                cy: section
                for cy, section in chunk.misc["java_sections"].items()
                if isinstance(cy, int) and isinstance(section, TAG_Compound)
            }
        else:
            return {}

    def _encode_block_section(
        self,
        chunk: Chunk,
        sections: Dict[int, TAG_Compound],
        palette: AnyNDArray,
        cy: int,
    ) -> bool:
        if cy in chunk.blocks:
            block_sub_array = palette[
                numpy.transpose(
                    chunk.blocks.get_sub_chunk(cy), (1, 2, 0)
                ).ravel()  # XYZ -> YZX
            ]

            data_sub_array = block_sub_array[:, 1]
            block_sub_array = block_sub_array[:, 0]
            # if not numpy.any(block_sub_array) and not numpy.any(data_sub_array):
            #     return False
            section = sections.setdefault(cy, TAG_Compound())
            section["Blocks"] = TAG_Byte_Array(block_sub_array.astype("uint8"))
            section["Data"] = TAG_Byte_Array(
                world_utils.to_nibble_array(data_sub_array)
            )
            return True
        return False

    def _encode_blocks(
        self,
        chunk: Chunk,
        sections: Dict[int, TAG_Compound],
        palette: AnyNDArray,
        bounds: Tuple[int, int],
    ):
        for cy in range(bounds[0] >> 4, bounds[1] >> 4):
            if not self._encode_block_section(chunk, sections, palette, cy):
                # In 1.13.2 and before if the Blocks key does not exist but the sub-chunk TAG_Compound does
                # exist the game will error and recreate the chunk. All sub-chunks that do not contain data
                # must be deleted.
                if cy in sections:
                    del sections[cy]

    @staticmethod
    def _encode_coords(chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]):
        level["xPos"] = TAG_Int(chunk.cx)
        level["zPos"] = TAG_Int(chunk.cz)

    @staticmethod
    def _encode_last_update(chunk: Chunk, level: TAG_Compound):
        level["LastUpdate"] = TAG_Long(chunk.misc.get("last_update", 0))

    def _encode_status(self, chunk: Chunk, level: TAG_Compound):
        status = chunk.status.as_type(StatusFormats.Raw)
        level["TerrainPopulated"] = TAG_Byte(int(status > -0.3))
        level["LightPopulated"] = TAG_Byte(int(status > -0.2))

    @staticmethod
    def _encode_v_tag(chunk: Chunk, level: TAG_Compound):
        level["V"] = TAG_Byte(chunk.misc.get("V", 1))

    def _encode_inhabited_time(self, chunk: Chunk, level: TAG_Compound):
        level["InhabitedTime"] = TAG_Long(chunk.misc.get("inhabited_time", 0))

    def _encode_biomes(
        self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    ):
        chunk.biomes.convert_to_2d()
        level["Biomes"] = TAG_Byte_Array(chunk.biomes.astype(dtype=numpy.uint8).ravel())

    def _encode_height(
        self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    ):
        height = chunk.misc.get("height_map256IA", None)
        if (
            isinstance(height, numpy.ndarray)
            and numpy.issubdtype(height.dtype, numpy.integer)
            and height.shape == (16, 16)
        ):
            level["HeightMap"] = TAG_Int_Array(height.ravel())
        elif self._features["height_map"] == "256IARequired":
            level["HeightMap"] = TAG_Int_Array(numpy.zeros(256, dtype=numpy.uint32))

    def _encode_entities(self, chunk: Chunk, level: TAG_Compound):
        if amulet.entity_support:
            level[self.Entities] = self._encode_entity_list(chunk.entities)
        else:
            level[self.Entities] = self._encode_entity_list(
                chunk.misc.get("java_entities_temp", TAG_List())
            )

    def _encode_block_entities(self, chunk: Chunk, level: TAG_Compound):
        level[self.BlockEntities] = self._encode_block_entity_list(chunk.block_entities)

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
        self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]
    ):
        level["TileTicks"] = self._encode_ticks(chunk.misc.get("block_ticks", {}))

    def _encode_sections(
        self, chunk: Chunk, sections: Dict[int, TAG_Compound], bounds: Tuple[int, int]
    ):
        self._encode_block_light(chunk, sections)
        self._encode_sky_light(chunk, sections)

    def _pack_light(
        self,
        chunk: Chunk,
        sections: Dict[int, TAG_Compound],
        feature_key: str,
        section_key: str,
    ):
        light_container = chunk.misc.get(feature_key, {})
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
                section[section_key] = TAG_Byte_Array(light[::2] + (light[1::2] << 4))
            elif self._features["light_optional"] == "false":
                section[section_key] = TAG_Byte_Array(
                    numpy.full(2048, 255, dtype=numpy.uint8)
                )

    def _encode_block_light(self, chunk: Chunk, sections: Dict[int, TAG_Compound]):
        self._pack_light(chunk, sections, "block_light", "BlockLight")

    def _encode_sky_light(self, chunk: Chunk, sections: Dict[int, TAG_Compound]):
        self._pack_light(chunk, sections, "sky_light", "SkyLight")


export = AnvilNAInterface

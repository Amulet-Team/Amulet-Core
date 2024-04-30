from __future__ import annotations

import logging
from typing import Tuple, Dict, Iterator, TYPE_CHECKING

import numpy
from amulet_nbt import (
    ByteTag,
    IntTag,
    LongTag,
    StringTag,
    ListTag,
    CompoundTag,
    ByteArrayTag,
    IntArrayTag,
    AbstractBaseArrayTag,
    NamedTag,
)

import amulet
from amulet.api.data_types import SubChunkNDArray, AnyNDArray, BlockCoordinates
from amulet.utils import world_utils
from amulet.api.wrapper import EntityIDType, EntityCoordType
from amulet.api.chunk import Chunk, StatusFormats
from .base_anvil_interface import (
    BaseAnvilInterface,
    ChunkDataType,
    ChunkPathType,
)

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

log = logging.getLogger(__name__)


class AnvilNAInterface(BaseAnvilInterface):
    Level: ChunkPathType = ("region", [("Level", CompoundTag)], CompoundTag)
    Sections: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("Sections", ListTag)],
        ListTag,
    )

    BlockTicks: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("TileTicks", ListTag)],
        ListTag,
    )

    def __init__(self):
        super().__init__()

        self._set_feature("light_optional", "false")

        self._register_decoder(self._decode_biomes)
        self._register_decoder(self._decode_blocks)
        self._register_decoder(self._decode_block_ticks)
        self._register_decoder(self._decode_block_light)
        self._register_decoder(self._decode_sky_light)

        self._register_encoder(self._encode_biomes)
        self._register_encoder(self._encode_blocks)
        self._register_encoder(self._encode_block_ticks)
        self._register_encoder(self._encode_block_light)
        self._register_encoder(self._encode_sky_light)

        self._register_post_encoder(self._post_encode_sections)

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

    @staticmethod
    def _init_decode(cx: int, cz: int, data: ChunkDataType) -> Chunk:
        """Get the decode started by creating a chunk object."""
        chunk = Chunk(cx, cz)
        chunk.misc = {
            # store the chunk data so that any non-versioned data can get saved back
            "_java_chunk_data_layers": data
        }
        return chunk

    def _get_level(self, data: ChunkDataType) -> CompoundTag:
        """
        Get the level data container
        For older levels this is region:Level but newer worlds it is in region root
        :param data: The raw chunk data
        :return: The level data compound
        """
        return self.get_layer_obj(data, self.Level)

    def _iter_sections(self, data: ChunkDataType) -> Iterator[Tuple[int, CompoundTag]]:
        sections: ListTag = self.get_layer_obj(data, self.Sections)
        for section in sections:
            yield section["Y"].py_int, section

    def _decode_blocks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        blocks: Dict[int, SubChunkNDArray] = {}
        palette = []
        palette_len = 0
        for cy, section in self._iter_sections(data):
            block_tag = section.pop("Blocks", None)
            data_tag = section.pop("Data", None)
            if not isinstance(block_tag, AbstractBaseArrayTag) or not isinstance(
                data_tag, AbstractBaseArrayTag
            ):
                continue
            section_blocks = numpy.asarray(block_tag, dtype=numpy.uint8)
            section_data = numpy.asarray(data_tag, dtype=numpy.uint8)
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks = section_blocks.astype(numpy.uint16)

            section_data = world_utils.from_nibble_array(section_data)
            section_data = section_data.reshape((16, 16, 16))

            add_tag = section.pop("Add", None)
            if isinstance(add_tag, AbstractBaseArrayTag):
                add_blocks = numpy.asarray(add_tag, dtype=numpy.uint8)
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
            if self.check_type(section, section_key, ByteArrayTag):
                light: numpy.ndarray = section.pop(section_key).np_array
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

    @staticmethod
    def _decode_ticks(ticks: ListTag) -> Dict[BlockCoordinates, Tuple[str, int, int]]:
        return {
            (tick["x"].py_data, tick["y"].py_data, tick["z"].py_data): (
                tick["i"].py_data,
                tick["t"].py_data,
                tick["p"].py_data,
            )
            for tick in ticks
            if all(c in tick and isinstance(tick[c], IntTag) for c in "xyztp")
            and "i" in tick
            and isinstance(tick["i"], StringTag)
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
            if isinstance(key, str) and isinstance(value, NamedTag)
        }

    def _get_encode_sections(
        self,
        data: ChunkDataType,
        floor_cy: int,
        height_cy: int,
    ) -> Dict[int, CompoundTag]:
        """Get or create the section array populating all valid sections"""
        sections: ListTag = self.set_layer_obj(data, self.Sections, setdefault=True)
        section_map: Dict[int, CompoundTag] = {}
        section: CompoundTag
        for section_index in range(len(sections) - 1, -1, -1):
            section = sections[section_index]
            cy = section.get("Y", None)
            if isinstance(cy, ByteTag):
                section_map[cy.py_int] = section
            else:
                sections.pop(section_index)
        for cy in range(floor_cy, floor_cy + height_cy):
            if cy not in section_map:
                section = section_map[cy] = CompoundTag({"Y": ByteTag(cy)})
                sections.append(section)
        return section_map

    def _encode_block_section(
        self,
        chunk: Chunk,
        sections: Dict[int, CompoundTag],
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
        sections[cy]["Blocks"] = ByteArrayTag(block_sub_array.astype("uint8"))
        sections[cy]["Data"] = ByteArrayTag(world_utils.to_nibble_array(data_sub_array))

    def _encode_blocks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        sections = self._get_encode_sections(data, floor_cy, height_cy)
        block_palette = chunk.misc.pop("block_palette")
        ceil_cy = floor_cy + height_cy
        for cy in chunk.blocks.sub_chunks:
            if floor_cy <= cy < ceil_cy:
                self._encode_block_section(chunk, sections, block_palette, cy)

    @staticmethod
    def _encode_ticks(ticks: Dict[BlockCoordinates, Tuple[str, int, int]]) -> ListTag:
        ticks_out = ListTag()
        if isinstance(ticks, dict):
            for k, v in ticks.items():
                try:
                    (x, y, z), (i, t, p) = k, v
                    ticks_out.append(
                        CompoundTag(
                            {
                                "i": StringTag(i),
                                "p": IntTag(p),
                                "t": IntTag(t),
                                "x": IntTag(x),
                                "y": IntTag(y),
                                "z": IntTag(x),
                            }
                        )
                    )
                except Exception:
                    log.error(f"Could not serialise tick data {k}: {v}")
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
                section[section_key] = ByteArrayTag(light[::2] + (light[1::2] << 4))
            elif self._features["light_optional"] == "false":
                section[section_key] = ByteArrayTag(
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

    def _post_encode_sections(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        """Strip out all empty sections"""
        sections = self.get_layer_obj(data, self.Sections)
        if sections:
            for i in range(len(sections) - 1, -1, -1):
                section = sections[i]
                if "Blocks" not in section or "Data" not in section:
                    # in 1.12 if a section exists, Blocks and Data must exist
                    sections.pop(i)
        if not sections:
            # if no sections remain we can remove the sections data
            self.get_layer_obj(data, self.Sections, pop_last=True)


export = AnvilNAInterface

from __future__ import annotations

import logging
from typing import Dict, Set, Tuple, Iterable, Optional, TYPE_CHECKING

import numpy
from amulet_nbt import (
    CompoundTag,
    ListTag,
    StringTag,
    LongArrayTag,
    LongTag,
    ShortTag,
)

import amulet
from amulet.api.data_types import AnyNDArray, BlockCoordinates
from amulet.api.block import Block
from amulet.api.chunk import StatusFormats
from .base_anvil_interface import ChunkDataType, ChunkPathType
from .anvil_0 import Anvil0Interface as ParentInterface
from amulet.utils.world_utils import (
    decode_long_array,
    encode_long_array,
)

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

log = logging.getLogger(__name__)


class Anvil1444Interface(ParentInterface):
    """
    Moved TerrainPopulated and LightPopulated to Status
    Made blocks paletted
    Added more tick tags
    Added structures tag
    """

    TerrainPopulated = None
    LightPopulated = None
    Status: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("Status", StringTag)],
        StringTag("full"),
    )

    ToBeTicked: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("ToBeTicked", ListTag)],
        ListTag,
    )

    LiquidTicks: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("LiquidTicks", ListTag)],
        ListTag,
    )
    LiquidsToBeTicked: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("LiquidsToBeTicked", ListTag)],
        ListTag,
    )

    PostProcessing: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("PostProcessing", ListTag)],
        ListTag,
    )

    Structures: ChunkPathType = (
        "region",
        [("Level", CompoundTag), ("Structures", CompoundTag)],
        CompoundTag,
    )

    LongArrayDense = True

    def __init__(self):
        super().__init__()
        self._set_feature("status", StatusFormats.Java_13)

        self._register_decoder(self._decode_fluid_ticks)
        self._register_decoder(self._decode_post_processing)
        self._register_decoder(self._decode_structures)

        self._register_encoder(self._encode_fluid_ticks)
        self._register_encoder(self._encode_post_processing)
        self._register_encoder(self._encode_structures)

    @staticmethod
    def minor_is_valid(key: int):
        return 1444 <= key < 1466

    def _decode_status(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.status = self.get_layer_obj(data, self.Status, pop_last=True).py_str

    def _decode_block_section(
        self, section: CompoundTag
    ) -> Optional[Tuple[numpy.ndarray, list]]:
        if "Palette" not in section:  # 1.14 makes block_palette/blocks optional.
            return None
        section_palette = self._decode_block_palette(section.pop("Palette"))
        decoded = decode_long_array(
            section.get_long_array("BlockStates").np_array,
            4096,
            max(4, (len(section_palette) - 1).bit_length()),
            dense=self.LongArrayDense,
        ).astype(numpy.uint32)
        arr = numpy.transpose(decoded.reshape((16, 16, 16)), (2, 0, 1))
        return arr, section_palette

    def _decode_blocks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        blocks: Dict[int, numpy.ndarray] = {}
        palette = [Block(namespace="minecraft", base_name="air")]

        for cy, section in self._iter_sections(data):
            data = self._decode_block_section(section)
            if data is not None:
                arr, section_palette = data
                blocks[cy] = arr + len(palette)
                palette += section_palette

        np_palette, inverse = numpy.unique(palette, return_inverse=True)
        np_palette: numpy.ndarray
        inverse: numpy.ndarray
        inverse = inverse.astype(numpy.uint32)
        for cy in blocks:
            blocks[cy] = inverse[blocks[cy]]
        chunk.blocks = blocks
        chunk.misc["block_palette"] = np_palette

    @staticmethod
    def _decode_block_palette(palette: ListTag) -> list:
        blockstates = []
        for entry in palette:
            namespace, base_name = entry.get_string("Name").py_str.split(":", 1)
            properties = entry.get_compound("Properties", CompoundTag({})).py_dict
            block = Block(
                namespace=namespace, base_name=base_name, properties=properties
            )
            blockstates.append(block)
        return blockstates

    @staticmethod
    def _decode_to_be_ticked(ticks: ListTag, floor_cy: int) -> Set[BlockCoordinates]:
        section_ticks: ListTag
        pos: ShortTag
        ticks_out = set()
        for cy, section_ticks in enumerate(ticks):
            block_cy = (floor_cy + cy) << 4
            for pos in section_ticks:
                pos_int = pos.py_int
                # TODO: check if these are correct. The order may be wrong.
                x = pos_int & 0xF
                y = (pos_int >> 4) & 0xF
                z = (pos_int >> 8) & 0xF
                ticks_out.add((x, block_cy + y, z))
        return ticks_out

    def _decode_block_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        super()._decode_block_ticks(chunk, data, floor_cy, height_cy)
        chunk.misc["to_be_ticked"] = self._decode_to_be_ticked(
            self.get_layer_obj(data, self.ToBeTicked, pop_last=True), floor_cy
        )

    def _decode_fluid_ticks(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, __):
        chunk.misc.setdefault("fluid_ticks", {}).update(
            self._decode_ticks(
                self.get_layer_obj(data, self.LiquidTicks, pop_last=True)
            )
        )
        chunk.misc["liquids_to_be_ticked"] = self._decode_to_be_ticked(
            self.get_layer_obj(data, self.LiquidsToBeTicked, pop_last=True), floor_cy
        )

    def _decode_post_processing(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["post_processing"] = self._decode_to_be_ticked(
            self.get_layer_obj(data, self.PostProcessing, pop_last=True), floor_cy
        )

    def _decode_structures(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        chunk.misc["structures"] = self.get_layer_obj(
            data, self.Structures, pop_last=True
        )

    def _encode_status(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        # Order the float value based on the order they would be run. Newer replacements for the same come just after
        # to save back find the next lowest valid value.
        status = chunk.status.as_type(self._features["status"])
        self.set_layer_obj(data, self.Status, StringTag(status))

    def _encode_inhabited_time(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data, self.InhabitedTime, LongTag(chunk.misc.get("inhabited_time", 0))
        )

    def _encode_block_section(
        self,
        chunk: Chunk,
        sections: Dict[int, CompoundTag],
        palette: AnyNDArray,
        cy: int,
    ) -> bool:
        block_sub_array = numpy.transpose(
            chunk.blocks.get_sub_chunk(cy), (1, 2, 0)
        ).ravel()

        sub_palette_, block_sub_array = numpy.unique(
            block_sub_array, return_inverse=True
        )
        sub_palette = self._encode_block_palette(palette[sub_palette_])
        if (
            len(sub_palette) == 1
            and sub_palette[0].get_string("Name").py_str == "minecraft:air"
        ):
            return False

        section = sections.setdefault(cy, CompoundTag())
        section["BlockStates"] = LongArrayTag(
            encode_long_array(
                block_sub_array, dense=self.LongArrayDense, min_bits_per_entry=4
            )
        )
        section["Palette"] = sub_palette

    @staticmethod
    def _encode_block_palette(blockstates: Iterable[Block]) -> ListTag:
        palette = ListTag()
        for block in blockstates:
            entry = CompoundTag()
            entry["Name"] = StringTag(f"{block.namespace}:{block.base_name}")
            if block.properties:
                string_properties = {
                    k: v
                    for k, v in block.properties.items()
                    if isinstance(v, StringTag)
                }
                if string_properties:
                    entry["Properties"] = CompoundTag(string_properties)
            palette.append(entry)
        return palette

    @staticmethod
    def _encode_to_be_ticked(
        ticks: Set[BlockCoordinates], floor_cy: int, height_cy: int
    ) -> ListTag:
        ceil_cy = floor_cy + height_cy
        ticks_out = ListTag([ListTag([], 2) for _ in range(floor_cy, ceil_cy)])
        if isinstance(ticks, set):
            for k in ticks:
                try:
                    (x, y, z) = k
                    cy = y >> 4
                    if floor_cy <= cy < ceil_cy:
                        x = x & 15
                        y = y & 15
                        z = z & 15
                        ticks_out[cy].append(ShortTag((z << 8) + (y << 4) + x))
                except Exception:
                    log.error(f"Could not serialise tick data {k}")
        return ticks_out

    def _encode_block_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        super()._encode_block_ticks(chunk, data, floor_cy, height_cy)
        self.set_layer_obj(
            data,
            self.ToBeTicked,
            self._encode_to_be_ticked(
                chunk.misc.get("to_be_ticked"), floor_cy, height_cy
            ),
        )

    def _encode_fluid_ticks(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data,
            self.LiquidTicks,
            self._encode_ticks(chunk.misc.get("fluid_ticks", {})),
        )
        self.set_layer_obj(
            data,
            self.LiquidsToBeTicked,
            self._encode_to_be_ticked(
                chunk.misc.get("liquids_to_be_ticked"), floor_cy, height_cy
            ),
        )

    def _encode_post_processing(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data,
            self.PostProcessing,
            self._encode_to_be_ticked(
                chunk.misc.get("post_processing"), floor_cy, height_cy
            ),
        )

    def _encode_structures(
        self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int
    ):
        self.set_layer_obj(
            data,
            self.Structures,
            chunk.misc.get(
                "structures",
                CompoundTag(
                    {
                        "References": CompoundTag(),
                        "Starts": CompoundTag(),
                    }
                ),
            ),
        )


export = Anvil1444Interface

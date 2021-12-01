from __future__ import annotations

from typing import Dict, Tuple, Optional, TYPE_CHECKING

import numpy
from amulet_nbt import (
    TAG_Compound,
    TAG_List,
    TAG_String,
    TAG_Long_Array,
    TAG_Long,
)

from amulet.api.data_types import AnyNDArray
from amulet.api.block import Block
from amulet.api.chunk import Blocks, StatusFormats
from .anvil_0 import Anvil0Interface
from amulet.utils.world_utils import (
    decode_long_array,
    encode_long_array,
)

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk


class Anvil1444Interface(Anvil0Interface):
    """
    Moved light and terrain populated to Status
    Made blocks paletted
    Added more tick tags
    Added structures tag
    """

    Structures = "Structures"
    LongArrayDense = True

    def __init__(self):
        super().__init__()
        self._set_feature("status", StatusFormats.Java_13)

    @staticmethod
    def minor_is_valid(key: int):
        return 1444 <= key < 1466

    def _decode_level(self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]):
        super()._decode_level(chunk, level, bounds)
        self._decode_fluid_ticks(chunk, level)
        self._decode_post_processing(chunk, level)
        self._decode_structures(chunk, level)

    def _decode_status(self, chunk: Chunk, compound: TAG_Compound):
        chunk.status = self.get_obj(
            compound, "Status", TAG_String, TAG_String("full")
        ).value

    def _decode_block_section(
        self, section: TAG_Compound
    ) -> Optional[Tuple[numpy.ndarray, list]]:
        if "Palette" not in section:  # 1.14 makes block_palette/blocks optional.
            return None
        section_palette = self._decode_block_palette(section.pop("Palette"))
        decoded = decode_long_array(
            section.pop("BlockStates").value,
            4096,
            max(4, (len(section_palette) - 1).bit_length()),
            dense=self.LongArrayDense,
        ).astype(numpy.uint32)
        arr = numpy.transpose(decoded.reshape((16, 16, 16)), (2, 0, 1))
        return arr, section_palette

    def _decode_blocks(
        self, chunk: Chunk, chunk_sections: Dict[int, TAG_Compound]
    ) -> AnyNDArray:
        blocks: Dict[int, numpy.ndarray] = {}
        palette = [Block(namespace="minecraft", base_name="air")]

        for cy, section in chunk_sections.items():
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
        return np_palette

    @staticmethod
    def _decode_block_palette(palette: TAG_List) -> list:
        blockstates = []
        for entry in palette:
            namespace, base_name = entry["Name"].value.split(":", 1)
            properties = entry.get("Properties", TAG_Compound({})).value
            block = Block(
                namespace=namespace, base_name=base_name, properties=properties
            )
            blockstates.append(block)
        return blockstates

    def _decode_block_ticks(self, chunk: Chunk, compound: TAG_Compound):
        super()._decode_block_ticks(chunk, compound)
        chunk.misc["to_be_ticked"] = self.get_obj(compound, "ToBeTicked", TAG_List)

    def _decode_fluid_ticks(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc.setdefault("fluid_ticks", {}).update(
            self._decode_ticks(self.get_obj(compound, "LiquidTicks", TAG_List))
        )
        chunk.misc["liquids_to_be_ticked"] = self.get_obj(
            compound, "LiquidsToBeTicked", TAG_List
        )

    def _decode_post_processing(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["post_processing"] = self.get_obj(
            compound, "PostProcessing", TAG_List
        )

    def _decode_structures(self, chunk: Chunk, compound: TAG_Compound):
        chunk.misc["structures"] = self.get_obj(compound, self.Structures, TAG_Compound)

    def _encode_level(self, chunk: Chunk, level: TAG_Compound, bounds: Tuple[int, int]):
        super()._encode_level(chunk, level, bounds)
        self._encode_fluid_ticks(chunk, level)
        self._encode_post_processing(chunk, level)
        self._encode_structures(chunk, level)

    def _encode_status(self, chunk: Chunk, level: TAG_Compound):
        # Order the float value based on the order they would be run. Newer replacements for the same come just after
        # to save back find the next lowest valid value.
        status = chunk.status.as_type(self._features["status"])
        level["Status"] = TAG_String(status)

    def _encode_inhabited_time(self, chunk: Chunk, level: TAG_Compound):
        level["InhabitedTime"] = TAG_Long(chunk.misc.get("inhabited_time", 0))

    def _encode_blocks(
        self,
        sections: Dict[int, TAG_Compound],
        blocks: Blocks,
        palette: AnyNDArray,
        cy_min: int,
        cy_max: int,
    ):
        for cy in range(cy_min, cy_max):
            if cy in blocks:
                block_sub_array = numpy.transpose(
                    blocks.get_sub_chunk(cy), (1, 2, 0)
                ).ravel()

                sub_palette_, block_sub_array = numpy.unique(
                    block_sub_array, return_inverse=True
                )
                sub_palette = self._encode_palette(palette[sub_palette_])
                if (
                    len(sub_palette) == 1
                    and sub_palette[0]["Name"].value == "minecraft:air"
                ):
                    continue

                section = sections.setdefault(cy, TAG_Compound())
                section["BlockStates"] = TAG_Long_Array(
                    encode_long_array(
                        block_sub_array, dense=self.LongArrayDense, min_bits_per_entry=4
                    )
                )
                section["Palette"] = sub_palette

    @staticmethod
    def _encode_palette(blockstates: list) -> TAG_List:
        palette = TAG_List()
        for block in blockstates:
            entry = TAG_Compound()
            entry["Name"] = TAG_String(f"{block.namespace}:{block.base_name}")
            if block.properties:
                entry["Properties"] = TAG_Compound(block.properties)
            palette.append(entry)
        return palette

    def _encode_block_ticks(self, chunk: Chunk, compound: TAG_Compound):
        super()._encode_block_ticks(chunk, compound)
        compound["ToBeTicked"] = chunk.misc.get(
            "to_be_ticked",
            TAG_List([TAG_List() for _ in range(16)]),
        )

    def _encode_fluid_ticks(self, chunk: Chunk, compound: TAG_Compound):
        compound["LiquidTicks"] = self._encode_ticks(chunk.misc.get("fluid_ticks", {}))
        compound["LiquidsToBeTicked"] = chunk.misc.get(
            "liquids_to_be_ticked",
            TAG_List([TAG_List() for _ in range(16)]),
        )

    def _encode_post_processing(self, chunk: Chunk, compound: TAG_Compound):
        compound["PostProcessing"] = chunk.misc.get(
            "post_processing",
            TAG_List([TAG_List() for _ in range(16)]),
        )

    def _encode_structures(self, chunk: Chunk, compound: TAG_Compound):
        compound["Structures"] = chunk.misc.get(
            "structures",
            TAG_Compound(
                {
                    "References": TAG_Compound(),
                    "Starts": TAG_Compound(),
                }
            ),
        )


export = Anvil1444Interface

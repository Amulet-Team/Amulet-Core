from __future__ import annotations

import os
import struct
from typing import Type, Union, Tuple, IO, List, Optional, Generator, Dict
import numpy

import amulet_nbt

from amulet import Block, BlockManager
from amulet.api.entity import Entity
from amulet.api.block_entity import BlockEntity
from amulet.api.selection import SelectionBox
from amulet.api.data_types import (
    ChunkCoordinates,
    BlockCoordinates,
)


class MCStructureSection:
    __slots__ = (
        "selection",
        "blocks",
        "palette",
        "shape",
        "entities",
        "block_entities",
    )

    def __init__(
            self,
            selection: SelectionBox,
            blocks: numpy.ndarray,
            palette: List[amulet_nbt.TAG_Compound],
            block_entities: List[amulet_nbt.TAG_Compound],
            entities: List[amulet_nbt.TAG_Compound]
    ):
        assert (
            selection.shape == blocks.shape
        ), "blocks shape does not match the specified section shape"
        self.selection = selection
        self.blocks = blocks
        self.palette = palette
        self.block_entities = block_entities
        self.entities = entities

    def __eq__(self, other):
        return (
            isinstance(other, MCStructureSection)
            and self.selection == other.selection
            and self.shape == other.shape
            and numpy.array_equal(self.blocks, other.blocks)
            and self.entities == other.entities
            and self.block_entities == other.block_entities
        )

    @property
    def location(self) -> BlockCoordinates:
        return self.selection.min


class MCStructureReader:
    def __init__(self, path_or_buffer: Union[str, IO]):
        if isinstance(path_or_buffer, str):
            assert path_or_buffer.endswith(".mcstructure"), "File selected is not a .mcstructure file"
            assert os.path.isfile(path_or_buffer), f"There is no mcstructure file at path {path_or_buffer}"
            mcstructure = amulet_nbt.load(path_or_buffer, little_endian=True)
        else:
            assert hasattr(path_or_buffer, "read"), "Object does not have a read method"
            mcstructure = amulet_nbt.load(buffer=path_or_buffer, little_endian=True)

        self._chunks: Dict[ChunkCoordinates, Tuple] = {}
        if mcstructure["format_version"].value == 1:
            min_point = numpy.array(tuple(c.value for c in mcstructure["structure_world_origin"]))
            max_point = min_point + tuple(c.value for c in mcstructure["size"])
            self._selection = SelectionBox(
                min_point,
                max_point
            )
            blocks_array: numpy.ndarray = numpy.array(
                [
                    [b.value for b in layer]
                    for layer in mcstructure["structure"]["block_indices"]
                ],
                dtype=numpy.int32
            ).reshape((len(mcstructure["structure"]["block_indices"]), *self._selection.shape))

            palette_key = list(mcstructure["structure"]["palette"].keys())[0]  # find a way to do this based on user input
            block_palette = list(mcstructure["structure"]["palette"][palette_key]["block_palette"])

            for cx, cz in self._selection.chunk_locations():
                chunk_box = SelectionBox.create_chunk_box(cx, cz).intersection(self._selection)
                array_slice = (slice(None), ) + chunk_box.create_moved_box(self._selection.min, subtract=True).slice
                chunk_blocks_: numpy.ndarray = blocks_array[array_slice]
                chunk_palette_indexes, chunk_blocks = numpy.unique(
                    chunk_blocks_.reshape((chunk_blocks_.shape[0], -1)).T,
                    return_inverse=True,
                    axis=0
                )

                chunk_palette = numpy.empty(len(chunk_palette_indexes), dtype=object)
                for palette_index, indexes in chunk_palette_indexes:
                    chunk_palette[palette_index] = tuple(block_palette[index] for index in indexes if index >= 0)

                self._chunks[(cx, cz)] = (chunk_box, chunk_blocks, chunk_palette, [], [])

            block_entities = {int(key): val["block_entity_data"] for key, val in mcstructure["structure"]["palette"][palette_key]["block_position_data"].items() if "block_entity_data" in val}
            for location, block_entity in block_entities.items():
                if all(key in block_entity for key in "xyz"):
                    x, y, z = block_entity["x"], block_entity["y"], block_entity["z"]
                    cx, cz = x >> 4, z >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[(cx, cz)][0]:
                        self._chunks[(cx, cz)][3].append(block_entity)

            entities = list(mcstructure["structure"]["entities"])
            for entity in entities:
                if "Pos" in entity:
                    x, y, z = entity["Pos"][0], entity["Pos"][1], entity["Pos"][2]
                    cx, cz = numpy.floor([x, z]) >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[(cx, cz)][0]:
                        self._chunks[(cx, cz)][4].append(entity)

        else:
            raise Exception(f"mcstructure file with format_version=={mcstructure['format_version'].value} cannot be read")



    @property
    def selection(self) -> SelectionBox:
        return self._selection

    @property
    def chunk_coords(self) -> Generator[ChunkCoordinates, None, None]:
        yield from self._chunks.keys()

    def close(self):
        pass


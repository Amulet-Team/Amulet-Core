from __future__ import annotations

import os
from typing import Union, Tuple, IO, List, Generator, Dict
import numpy

import amulet_nbt

from amulet.api.selection import SelectionBox
from amulet.api.data_types import ChunkCoordinates, BlockCoordinates, AnyNDArray
from amulet.api.errors import ChunkDoesNotExist
from amulet.utils.numpy_helpers import brute_sort_objects_no_hash


class MCStructureChunk:
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
        palette: AnyNDArray,
        block_entities: List[amulet_nbt.TAG_Compound],
        entities: List[amulet_nbt.TAG_Compound],
    ):
        assert isinstance(blocks, numpy.ndarray)
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
            isinstance(other, MCStructureChunk)
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
            assert path_or_buffer.endswith(
                ".mcstructure"
            ), "File selected is not a .mcstructure file"
            assert os.path.isfile(
                path_or_buffer
            ), f"There is no mcstructure file at path {path_or_buffer}"
            mcstructure = amulet_nbt.load(path_or_buffer, little_endian=True)
        else:
            assert hasattr(path_or_buffer, "read"), "Object does not have a read method"
            mcstructure = amulet_nbt.load(buffer=path_or_buffer, little_endian=True)

        self._chunks: Dict[
            ChunkCoordinates,
            Tuple[
                SelectionBox,
                numpy.ndarray,
                AnyNDArray,
                List[amulet_nbt.TAG_Compound],
                List[amulet_nbt.TAG_Compound],
            ],
        ] = {}
        if mcstructure["format_version"].value == 1:
            min_point = numpy.array(
                tuple(c.value for c in mcstructure["structure_world_origin"])
            )
            max_point = min_point + tuple(c.value for c in mcstructure["size"])
            self._selection = SelectionBox(min_point, max_point)
            blocks_array: numpy.ndarray = numpy.array(
                [
                    [b.value for b in layer]
                    for layer in mcstructure["structure"]["block_indices"]
                ],
                dtype=numpy.int32,
            ).reshape(
                (len(mcstructure["structure"]["block_indices"]), *self._selection.shape)
            )

            palette_key = list(mcstructure["structure"]["palette"].keys())[
                0
            ]  # find a way to do this based on user input
            block_palette = list(
                mcstructure["structure"]["palette"][palette_key]["block_palette"]
            )

            for cx, cz in self._selection.chunk_locations():
                chunk_box = SelectionBox.create_chunk_box(cx, cz).intersection(
                    self._selection
                )
                array_slice = (slice(None),) + chunk_box.create_moved_box(
                    self._selection.min, subtract=True
                ).slice
                chunk_blocks_: numpy.ndarray = blocks_array[array_slice]
                chunk_palette_indexes, chunk_blocks = numpy.unique(
                    chunk_blocks_.reshape((chunk_blocks_.shape[0], -1)).T,
                    return_inverse=True,
                    axis=0,
                )
                chunk_blocks = chunk_blocks.reshape(chunk_blocks_.shape[1:])

                chunk_palette = numpy.empty(len(chunk_palette_indexes), dtype=object)
                for palette_index, indexes in enumerate(chunk_palette_indexes):
                    chunk_palette[palette_index] = tuple(
                        block_palette[index] for index in indexes if index >= 0
                    )

                self._chunks[(cx, cz)] = (
                    chunk_box,
                    chunk_blocks,
                    chunk_palette,
                    [],
                    [],
                )

            block_entities = {
                int(key): val["block_entity_data"]
                for key, val in mcstructure["structure"]["palette"][palette_key][
                    "block_position_data"
                ].items()
                if "block_entity_data" in val
            }
            for location, block_entity in block_entities.items():
                if all(key in block_entity for key in "xyz"):
                    x, y, z = (
                        block_entity["x"].value,
                        block_entity["y"].value,
                        block_entity["z"].value,
                    )
                    cx, cz = x >> 4, z >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[(cx, cz)][
                        0
                    ]:
                        self._chunks[(cx, cz)][3].append(block_entity)

            entities = list(mcstructure["structure"]["entities"])
            for entity in entities:
                if "Pos" in entity:
                    x, y, z = (
                        entity["Pos"][0].value,
                        entity["Pos"][1].value,
                        entity["Pos"][2].value,
                    )
                    cx, cz = numpy.floor([x, z]).astype(numpy.int) >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[(cx, cz)][
                        0
                    ]:
                        self._chunks[(cx, cz)][4].append(entity)

        else:
            raise Exception(
                f"mcstructure file with format_version=={mcstructure['format_version'].value} cannot be read"
            )

    def read(self, cx: int, cz: int):
        if (cx, cz) in self._chunks:
            return MCStructureChunk(*self._chunks[(cx, cz)])
        else:
            raise ChunkDoesNotExist

    @property
    def selection(self) -> SelectionBox:
        return self._selection

    @property
    def chunk_coords(self) -> Generator[ChunkCoordinates, None, None]:
        yield from self._chunks.keys()

    def close(self):
        pass


class MCStructureWriter:
    def __init__(self, path_or_buffer: str, selection: SelectionBox):
        self._path_or_buffer = path_or_buffer
        self._selection = selection

        self._data = amulet_nbt.NBTFile(
            amulet_nbt.TAG_Compound(
                {
                    "format_version": amulet_nbt.TAG_Int(1),
                    "structure_world_origin": amulet_nbt.TAG_List(
                        [
                            amulet_nbt.TAG_Int(selection.min_x),
                            amulet_nbt.TAG_Int(selection.min_y),
                            amulet_nbt.TAG_Int(selection.min_z),
                        ]
                    ),
                    "size": amulet_nbt.TAG_List(
                        [
                            amulet_nbt.TAG_Int(selection.size_x),
                            amulet_nbt.TAG_Int(selection.size_y),
                            amulet_nbt.TAG_Int(selection.size_z),
                        ]
                    ),
                }
            )
        )

        self._entities = []
        self._block_entities = []
        self._blocks = numpy.zeros(
            selection.shape, dtype=numpy.uint32
        )  # only 12 bits are actually used at most
        self._palette: List[AnyNDArray] = []
        self._palette_len = 0

    def write(self, section: MCStructureChunk):
        if section.selection.intersects(self._selection):
            box = section.selection.create_moved_box(self._selection.min, subtract=True)
            self._blocks[box.slice] = section.blocks + self._palette_len
            self._palette.append(section.palette)
            self._palette_len += len(section.palette)
            self._block_entities += section.block_entities
            self._entities += section.entities

    def close(self):
        compact_palette, lut = brute_sort_objects_no_hash(
            numpy.concatenate(self._palette)
        )
        self._blocks = lut[self._blocks].ravel()
        block_palette = []
        block_palette_indices = []
        for block_list in compact_palette:
            indexed_block = [-1] * 2
            for block_layer, block in enumerate(block_list):
                if block_layer >= 2:
                    break
                if block in block_palette:
                    indexed_block[block_layer] = block_palette.index(block)
                else:
                    indexed_block[block_layer] = len(block_palette)
                    block_palette.append(block)
            block_palette_indices.append(indexed_block)

        block_indices = numpy.array(block_palette_indices, dtype=numpy.int32)[
            self._blocks
        ].T

        self._data["structure"] = amulet_nbt.TAG_Compound(
            {
                "block_indices": amulet_nbt.TAG_List(
                    [  # a list of tag ints that index into the block_palette. One list per block layer
                        amulet_nbt.TAG_List(
                            [amulet_nbt.TAG_Int(block) for block in layer]
                        )
                        for layer in block_indices
                    ]
                ),
                "entities": amulet_nbt.TAG_List(self._entities),
                "palette": amulet_nbt.TAG_Compound(
                    {
                        "default": amulet_nbt.TAG_Compound(
                            {
                                "block_palette": amulet_nbt.TAG_List(block_palette),
                                "block_position_data": amulet_nbt.TAG_Compound(
                                    {
                                        str(
                                            (
                                                (
                                                    block_entity["x"].value
                                                    - self._selection.min_x
                                                )
                                                * self._selection.size_y
                                                + (
                                                    block_entity["y"].value
                                                    - self._selection.min_y
                                                )
                                            )
                                            * self._selection.size_z
                                            + block_entity["z"].value
                                            - self._selection.min_z
                                        ): amulet_nbt.TAG_Compound(
                                            {"block_entity_data": block_entity}
                                        )
                                        for block_entity in self._block_entities
                                    }
                                ),
                            }
                        )
                    }
                ),
            }
        )
        self._data.save_to(self._path_or_buffer, compressed=False, little_endian=True)

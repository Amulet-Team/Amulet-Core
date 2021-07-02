import os
from typing import Optional, Tuple, Iterable, TYPE_CHECKING, BinaryIO, Dict, List, Union
import numpy
import copy

import amulet_nbt

from amulet.api.data_types import (
    VersionNumberAny,
    ChunkCoordinates,
    AnyNDArray,
    Dimension,
    PlatformType,
)
from amulet.api.wrapper import StructureFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ChunkDoesNotExist, ObjectWriteError
from amulet.utils.numpy_helpers import brute_sort_objects_no_hash

from .chunk import MCStructureChunk
from .interface import MCStructureInterface

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface

mcstructure_interface = MCStructureInterface()


class MCStructureFormatWrapper(StructureFormatWrapper):
    """
    This FormatWrapper class exists to interface with the Bedrock mcstructure structure block format.
    """

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`MCStructureFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)
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

    def _create(
        self,
        overwrite: bool,
        bounds: Union[
            SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None
        ] = None,
        **kwargs,
    ):
        if not overwrite and os.path.isfile(self.path):
            raise ObjectWriteError(f"There is already a file at {self.path}")
        translator_version = self.translation_manager.get_version(
            "bedrock", (999, 999, 999)
        )
        self._platform = translator_version.platform
        self._version = translator_version.version_number
        self._chunks = {}
        self._set_selection(bounds)
        self._is_open = True
        self._has_lock = True

    def open_from(self, f: BinaryIO):
        mcstructure = amulet_nbt.load(f, little_endian=True)
        if mcstructure["format_version"].value == 1:
            min_point = numpy.array(
                tuple(c.value for c in mcstructure["structure_world_origin"])
            )
            max_point = min_point + tuple(c.value for c in mcstructure["size"])
            selection = SelectionBox(min_point, max_point)
            self._bounds[self.dimensions[0]] = SelectionGroup(selection)
            translator_version = self.translation_manager.get_version(
                "bedrock", (999, 999, 999)
            )
            self._platform = translator_version.platform
            self._version = translator_version.version_number
            blocks_array: numpy.ndarray = numpy.array(
                [
                    [b.value for b in layer]
                    for layer in mcstructure["structure"]["block_indices"]
                ],
                dtype=numpy.int32,
            ).reshape(
                (len(mcstructure["structure"]["block_indices"]), *selection.shape)
            )

            palette_key = list(mcstructure["structure"]["palette"].keys())[
                0
            ]  # find a way to do this based on user input
            block_palette = list(
                mcstructure["structure"]["palette"][palette_key]["block_palette"]
            )

            if -1 in blocks_array[0]:
                blocks_array[0][blocks_array[0] == -1] = len(block_palette)
                block_palette.append(
                    amulet_nbt.TAG_Compound(
                        {
                            "name": amulet_nbt.TAG_String("minecraft:structure_void"),
                            "states": amulet_nbt.TAG_Compound(),
                            "version": amulet_nbt.TAG_Int(17694723),  # 1.13.0
                        }
                    )
                )

            for cx, cz in selection.chunk_locations():
                chunk_box = SelectionBox.create_chunk_box(cx, cz).intersection(
                    selection
                )
                array_slice = (slice(None),) + chunk_box.create_moved_box(
                    selection.min, subtract=True
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
                    cx, cz = numpy.floor([x, z]).astype(int) >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[(cx, cz)][
                        0
                    ]:
                        self._chunks[(cx, cz)][4].append(entity)

        else:
            raise Exception(
                f"mcstructure file with format_version=={mcstructure['format_version'].value} cannot be read"
            )

    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isfile(path) and path.endswith(".mcstructure")

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"bedrock": (False, True)}

    @property
    def extensions(self) -> Tuple[str, ...]:
        return (".mcstructure",)

    def _get_interface(self, raw_chunk_data=None) -> "MCStructureInterface":
        return mcstructure_interface

    def _get_interface_and_translator(
        self, raw_chunk_data=None
    ) -> Tuple["Interface", "Translator", VersionNumberAny]:
        interface = self._get_interface(raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            self.max_world_version, raw_chunk_data, self.translation_manager
        )
        return interface, translator, version_identifier

    def save_to(self, f: BinaryIO):
        selection = self._bounds[self.dimensions[0]].selection_boxes[0]
        data = amulet_nbt.NBTFile(
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

        entities = []
        block_entities = []
        blocks = numpy.zeros(selection.shape, dtype=numpy.uint32)
        palette: List[AnyNDArray] = []
        if self.version < (1, 13, 0):
            raise Exception(
                "Writing to mcstructre files in pre-1.13 format is not currently supported."
            )
        else:
            arr = numpy.empty(1, dtype=object)
            arr[0] = [
                amulet_nbt.TAG_Compound(
                    {
                        "name": amulet_nbt.TAG_String("minecraft:air"),
                        "states": amulet_nbt.TAG_Compound(),
                        "version": amulet_nbt.TAG_Int(17694723),
                    }
                )
            ]
            palette.append(arr)

        palette_len = 1

        for (
            selection_,
            blocks_,
            palette_,
            block_entities_,
            entities_,
        ) in self._chunks.values():
            if selection_.intersects(selection):
                box = selection_.create_moved_box(selection.min, subtract=True)
                blocks[box.slice] = blocks_ + palette_len
                palette.append(palette_)
                palette_len += len(palette_)
                block_entities += block_entities_
                entities += entities_

        compact_palette, lut = brute_sort_objects_no_hash(numpy.concatenate(palette))
        blocks = lut[blocks].ravel()
        block_palette = []
        block_palette_indices = []
        for block_list in compact_palette:
            indexed_block = [-1] * 2
            for block_layer, block in enumerate(block_list):
                if block_layer >= 2:
                    break
                if block["name"] != "minecraft:structure_void":
                    if block in block_palette:
                        indexed_block[block_layer] = block_palette.index(block)
                    else:
                        indexed_block[block_layer] = len(block_palette)
                        block_palette.append(block)
            block_palette_indices.append(indexed_block)

        block_indices = numpy.array(block_palette_indices, dtype=numpy.int32)[blocks].T

        data["structure"] = amulet_nbt.TAG_Compound(
            {
                "block_indices": amulet_nbt.TAG_List(
                    [  # a list of tag ints that index into the block_palette. One list per block layer
                        amulet_nbt.TAG_List(
                            [amulet_nbt.TAG_Int(block) for block in layer]
                        )
                        for layer in block_indices
                    ]
                ),
                "entities": amulet_nbt.TAG_List(entities),
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
                                                    - selection.min_x
                                                )
                                                * selection.size_y
                                                + (
                                                    block_entity["y"].value
                                                    - selection.min_y
                                                )
                                            )
                                            * selection.size_z
                                            + block_entity["z"].value
                                            - selection.min_z
                                        ): amulet_nbt.TAG_Compound(
                                            {"block_entity_data": block_entity}
                                        )
                                        for block_entity in block_entities
                                    }
                                ),
                            }
                        )
                    }
                ),
            }
        )
        data.save_to(f, compressed=False, little_endian=True)

    def _close(self):
        """Close the disk database"""
        self._chunks.clear()

    def unload(self):
        pass

    def all_chunk_coords(
        self, dimension: Optional[Dimension] = None
    ) -> Iterable[ChunkCoordinates]:
        yield from self._chunks.keys()

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return (cx, cz) in self._chunks

    def _encode(
        self,
        interface: MCStructureInterface,
        chunk: Chunk,
        dimension: Dimension,
        chunk_palette: AnyNDArray,
    ):
        return interface.encode(
            chunk,
            chunk_palette,
            self.max_world_version,
            SelectionBox.create_chunk_box(chunk.cx, chunk.cz).intersection(
                self._bounds[dimension].to_box()
            ),
        )

    def _delete_chunk(self, cx: int, cz: int, dimension: Optional[Dimension] = None):
        if (cx, cz) in self._chunks:
            del self._chunks[(cx, cz)]

    def _put_raw_chunk_data(
        self,
        cx: int,
        cz: int,
        section: MCStructureChunk,
        dimension: Optional[Dimension] = None,
    ):
        self._chunks[(cx, cz)] = copy.deepcopy(
            (
                section.selection,
                section.blocks,
                section.palette,
                section.block_entities,
                section.entities,
            )
        )

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: Optional[Dimension] = None
    ) -> MCStructureChunk:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        if (cx, cz) in self._chunks:
            return MCStructureChunk(*copy.deepcopy(self._chunks[(cx, cz)]))
        else:
            raise ChunkDoesNotExist

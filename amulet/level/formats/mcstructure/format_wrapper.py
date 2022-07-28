import os
from typing import Optional, Tuple, Iterable, TYPE_CHECKING, BinaryIO, Dict, List, Union
import numpy
import copy

from amulet_nbt import (
    IntTag,
    StringTag,
    ListTag,
    CompoundTag,
    load as load_nbt,
    utf8_escape_decoder,
    utf8_escape_encoder,
)

from amulet.api.data_types import (
    VersionNumberAny,
    VersionNumberTuple,
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


class MCStructureFormatWrapper(StructureFormatWrapper[VersionNumberTuple]):
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
                List[CompoundTag],
                List[CompoundTag],
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
        mcstructure = load_nbt(
            f, little_endian=True, string_decoder=utf8_escape_decoder
        ).compound
        if mcstructure.get_int("format_version").py_int == 1:
            min_point = numpy.array(
                tuple(c.py_int for c in mcstructure.get_list("structure_world_origin"))
            )
            max_point = min_point + tuple(
                c.py_int for c in mcstructure.get_list("size")
            )
            selection = SelectionBox(min_point, max_point)
            self._bounds[self.dimensions[0]] = SelectionGroup(selection)
            translator_version = self.translation_manager.get_version(
                "bedrock", (999, 999, 999)
            )
            self._platform = translator_version.platform
            self._version = translator_version.version_number
            structure = mcstructure.get_compound("structure")
            indices = structure.get_list("block_indices")
            blocks_array: numpy.ndarray = numpy.array(
                [[b.py_int for b in layer] for layer in indices],
                dtype=numpy.int32,
            ).reshape((len(indices), *selection.shape))

            palette_tag = structure.get_compound("palette")
            palette_key = next(iter(palette_tag))
            sub_palette_tag = palette_tag.get_compound(palette_key)
            block_palette = list(sub_palette_tag.get_list("block_palette"))

            if -1 in blocks_array[0]:
                blocks_array[0][blocks_array[0] == -1] = len(block_palette)
                block_palette.append(
                    CompoundTag(
                        {
                            "name": StringTag("minecraft:structure_void"),
                            "states": CompoundTag(),
                            "version": IntTag(17694723),  # 1.13.0
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
                for key, val in sub_palette_tag.get_compound(
                    "block_position_data"
                ).items()
                if "block_entity_data" in val
            }
            for location, block_entity in block_entities.items():
                if all(key in block_entity for key in "xyz"):
                    x, y, z = (
                        block_entity["x"].py_int,
                        block_entity["y"].py_int,
                        block_entity["z"].py_int,
                    )
                    cx, cz = x >> 4, z >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[(cx, cz)][
                        0
                    ]:
                        self._chunks[(cx, cz)][3].append(block_entity)

            for entity in structure.get_list("entities"):
                if "Pos" in entity:
                    pos = entity.get_list("Pos")
                    x = pos[0].py_float
                    y = pos[1].py_float
                    z = pos[2].py_float
                    cx, cz = numpy.floor([x, z]).astype(int) >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[(cx, cz)][
                        0
                    ]:
                        self._chunks[(cx, cz)][4].append(entity)

        else:
            raise Exception(
                f"mcstructure file with format_version=={mcstructure.get_int('format_version').py_int} cannot be read"
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
        mcstructure = CompoundTag(
            {
                "format_version": IntTag(1),
                "structure_world_origin": ListTag(
                    [
                        IntTag(selection.min_x),
                        IntTag(selection.min_y),
                        IntTag(selection.min_z),
                    ]
                ),
                "size": ListTag(
                    [
                        IntTag(selection.size_x),
                        IntTag(selection.size_y),
                        IntTag(selection.size_z),
                    ]
                ),
            }
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
                CompoundTag(
                    {
                        "name": StringTag("minecraft:air"),
                        "states": CompoundTag(),
                        "version": IntTag(17694723),
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
                if block["name"] != StringTag("minecraft:structure_void"):
                    if block in block_palette:
                        indexed_block[block_layer] = block_palette.index(block)
                    else:
                        indexed_block[block_layer] = len(block_palette)
                        block_palette.append(block)
            block_palette_indices.append(indexed_block)

        block_indices = numpy.array(block_palette_indices, dtype=numpy.int32)[blocks].T

        mcstructure["structure"] = CompoundTag(
            {
                "block_indices": ListTag(
                    [  # a list of tag ints that index into the block_palette. One list per block layer
                        ListTag([IntTag(block) for block in layer])
                        for layer in block_indices
                    ]
                ),
                "entities": ListTag(entities),
                "palette": CompoundTag(
                    {
                        "default": CompoundTag(
                            {
                                "block_palette": ListTag(block_palette),
                                "block_position_data": CompoundTag(
                                    {
                                        str(
                                            (
                                                (
                                                    block_entity["x"].py_int
                                                    - selection.min_x
                                                )
                                                * selection.size_y
                                                + (
                                                    block_entity["y"].py_int
                                                    - selection.min_y
                                                )
                                            )
                                            * selection.size_z
                                            + block_entity["z"].py_int
                                            - selection.min_z
                                        ): CompoundTag(
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
        mcstructure.save_to(
            f, compressed=False, little_endian=True, string_encoder=utf8_escape_encoder
        )

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

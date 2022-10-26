import os
from typing import Optional, Tuple, Iterable, TYPE_CHECKING, BinaryIO, Dict, List, Union
import numpy
import copy

from amulet_nbt import (
    ShortTag,
    IntTag,
    ListTag,
    CompoundTag,
    ByteArrayTag,
    IntArrayTag,
    NamedTag,
    load as load_nbt,
)

from amulet.api.data_types import (
    VersionNumberAny,
    VersionNumberInt,
    ChunkCoordinates,
    AnyNDArray,
    Dimension,
    PlatformType,
)
from amulet.api.wrapper import StructureFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ChunkDoesNotExist, ObjectWriteError, ObjectReadError
from amulet.api.block import Block
from amulet.utils.numpy_helpers import brute_sort_objects_no_hash

from .chunk import SpongeSchemChunk
from .interface import SpongeSchemInterface
from .varint import decode_byte_array, encode_array

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface


class SpongeSchemReadError(ObjectReadError):
    pass


class SpongeSchemWriteError(ObjectWriteError):
    pass


sponge_schem_interface = SpongeSchemInterface()

max_schem_version = 2


class SpongeSchemFormatWrapper(StructureFormatWrapper[VersionNumberInt]):
    """
    This FormatWrapper class exists to interface with the sponge schematic structure format.
    """

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`SpongeSchemFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)
        self._chunks: Dict[
            ChunkCoordinates,
            SpongeSchemChunk,
        ] = {}
        self._schem_version: int = max_schem_version

    def _create(
        self,
        overwrite: bool,
        bounds: Union[
            SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None
        ] = None,
        **kwargs,
    ):
        if not overwrite and os.path.isfile(self.path):
            raise SpongeSchemWriteError(f"There is already a file at {self.path}")
        translator_version = self.translation_manager.get_version("java", self._version)
        self._platform = translator_version.platform
        self._version = translator_version.data_version
        self._chunks = {}
        self._set_selection(bounds)
        self._is_open = True
        self._has_lock = True

    def open_from(self, f: BinaryIO):
        sponge_schem = load_nbt(f).compound
        version_tag = sponge_schem.get("Version")
        if not isinstance(version_tag, IntTag):
            raise SpongeSchemReadError("Version key must exist and be an integer.")
        version = version_tag.py_int
        if version == 1:
            raise SpongeSchemReadError(
                "Sponge Schematic Version 1 is not supported currently."
            )
        elif version == 2:
            offset = sponge_schem.get("Offset")
            if isinstance(offset, IntArrayTag) and len(offset) == 3:
                min_point = numpy.array(offset)
            else:
                min_point = numpy.array([0, 0, 0], dtype=numpy.int32)

            size = []
            for key in ("Width", "Height", "Length"):
                val = sponge_schem.get(key)
                if not isinstance(val, ShortTag):
                    raise SpongeSchemReadError(
                        f"Key {key} must exist and be a ShortTag."
                    )
                # convert to an unsigned short
                val = val.py_int
                if val < 0:
                    val += 2**16
                size.append(val)

            max_point = min_point + size
            selection = SelectionBox(min_point, max_point)
            self._bounds[self.dimensions[0]] = SelectionGroup(selection)
            data_version = sponge_schem.get("DataVersion")
            if not isinstance(data_version, IntTag):
                raise SpongeSchemReadError("DataVersion must be a IntTag.")
            translator_version = self.translation_manager.get_version(
                "java", int(data_version)
            )
            self._platform = translator_version.platform
            self._version = translator_version.data_version

            packed_block_data = sponge_schem.get("BlockData")
            if not isinstance(packed_block_data, ByteArrayTag):
                raise SpongeSchemReadError("BlockData must be a ByteArrayTag")

            unpacked_block_data = decode_byte_array(
                numpy.array(packed_block_data, dtype=numpy.uint8)
            )
            if len(unpacked_block_data) != numpy.prod(size):
                raise SpongeSchemReadError(
                    "The data contained in BlockData does not match the size of the schematic."
                )
            dx, dy, dz = selection.shape
            blocks_array: numpy.ndarray = numpy.transpose(
                numpy.array(
                    unpacked_block_data,
                    dtype=numpy.uint32,
                ).reshape((dy, dz, dx)),
                (2, 0, 1),  # YZX => XYZ
            )

            if "Palette" not in sponge_schem:
                raise SpongeSchemReadError(
                    "Amulet is not able to read Sponge Schem files with no block palette."
                )

            palette_data = sponge_schem.get("Palette")
            if not isinstance(palette_data, CompoundTag):
                raise SpongeSchemReadError("Palette must be a CompoundTag.")

            block_palette: Dict[int, Block] = {}
            for blockstate, index_tag in palette_data.items():
                index = index_tag.py_int
                if index in block_palette:
                    raise SpongeSchemReadError(
                        f"Duplicate block index {index} found in the palette."
                    )
                block_palette[index] = Block.from_string_blockstate(blockstate)

            if not numpy.all(numpy.isin(blocks_array, list(block_palette))):
                raise SpongeSchemReadError(
                    "Some values in BlockData were not present in Palette"
                )

            for cx, cz in selection.chunk_locations():
                chunk_box = SelectionBox.create_chunk_box(cx, cz).intersection(
                    selection
                )
                array_slice = chunk_box.create_moved_box(
                    selection.min, subtract=True
                ).slice
                chunk_blocks_: numpy.ndarray = blocks_array[array_slice]
                chunk_palette_indexes, chunk_blocks = numpy.unique(
                    chunk_blocks_,
                    return_inverse=True,
                )
                chunk_blocks = chunk_blocks.reshape(chunk_blocks_.shape)

                chunk_palette = numpy.empty(len(chunk_palette_indexes), dtype=object)
                for palette_index, index in enumerate(chunk_palette_indexes):
                    chunk_palette[palette_index] = block_palette[index]

                self._chunks[(cx, cz)] = SpongeSchemChunk(
                    chunk_box,
                    chunk_blocks,
                    chunk_palette,
                    [],
                    [],
                )

            if "BlockEntities" in sponge_schem:
                block_entities = sponge_schem["BlockEntities"]
                if (
                    not isinstance(block_entities, ListTag)
                    or block_entities.list_data_type != 10  # CompoundTag.tag_id
                ):
                    raise SpongeSchemReadError(
                        "BlockEntities must be a ListTag of compound tags."
                    )

                for block_entity in block_entities:
                    if "Pos" not in block_entity:
                        continue

                    pos_tag = block_entity["Pos"]
                    if not (isinstance(pos_tag, IntArrayTag) and len(pos_tag) == 3):
                        continue

                    pos = pos_tag.np_array + min_point
                    x, y, z = pos
                    block_entity["Pos"] = IntArrayTag(pos)
                    cx, cz = x >> 4, z >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[
                        (cx, cz)
                    ].selection:
                        self._chunks[(cx, cz)].block_entities.append(block_entity)

            if "Entities" in sponge_schem:
                entities = sponge_schem["Entities"]
                if (
                    not isinstance(entities, ListTag)
                    or entities.list_data_type != 10  # CompoundTag.tag_id
                ):
                    raise SpongeSchemReadError(
                        "Entities must be a ListTag of compound tags."
                    )

                for entity in entities:
                    if "Pos" not in entity:
                        continue

                    pos = entity["Pos"]
                    if not (
                        isinstance(pos, ListTag)
                        and len(pos) == 3
                        and pos.list_data_type == 6
                    ):  # DoubleTag.tag_id:
                        continue

                    x, y, z = (
                        pos[0].py_float + offset[0],
                        pos[1].py_float + offset[0],
                        pos[2].py_float + offset[0],
                    )
                    entity["Pos"] = ListTag(
                        [
                            IntTag(x),
                            IntTag(y),
                            IntTag(z),
                        ]
                    )
                    cx, cz = numpy.floor([x, z]).astype(int) >> 4
                    if (cx, cz) in self._chunks and (x, y, z) in self._chunks[
                        (cx, cz)
                    ].selection:
                        self._chunks[(cx, cz)].entities.append(entity)

        else:
            raise SpongeSchemReadError(
                f"Sponge Schematic Version {version} is not supported currently."
            )

    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isfile(path) and path.endswith(".schem")

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"java": (False, True)}

    @property
    def extensions(self) -> Tuple[str, ...]:
        return (".schem",)

    def _get_interface(self, raw_chunk_data=None) -> "SpongeSchemInterface":
        return sponge_schem_interface

    def _get_interface_and_translator(
        self, raw_chunk_data=None
    ) -> Tuple["Interface", "Translator", VersionNumberAny]:
        interface = self._get_interface(raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            self.max_world_version, raw_chunk_data, self.translation_manager
        )
        return interface, translator, version_identifier

    def save_to(self, f: BinaryIO):
        if self._schem_version == 1:
            raise SpongeSchemReadError(
                "Sponge Schematic Version 1 is not supported currently."
            )
        elif self._schem_version == 2:
            selection = self._bounds[self.dimensions[0]].selection_boxes[0]
            if any(s > 2**16 - 1 for s in selection.shape):
                raise SpongeSchemWriteError(
                    "The structure is too large to be exported to a Sponge Schematic file. It must be 2^16 - 1 at most in each dimension."
                )
            overflowed_shape = [
                s if s < 2**15 else s - 2**16 for s in selection.shape
            ]
            tag = CompoundTag(
                {
                    "Version": IntTag(2),
                    "DataVersion": IntTag(self._version),
                    "Width": ShortTag(overflowed_shape[0]),
                    "Height": ShortTag(overflowed_shape[1]),
                    "Length": ShortTag(overflowed_shape[2]),
                    "Offset": IntArrayTag(selection.min),
                }
            )

            entities = []
            block_entities = []
            blocks = numpy.zeros(selection.shape, dtype=numpy.uint32)
            palette: List[AnyNDArray] = []
            if self._version < 1500:
                raise Exception(
                    "Writing to Sponge Schematic files in pre-1.13 format is not currently supported."
                )
            else:
                arr = numpy.empty(1, dtype=object)
                arr[0] = Block("minecraft", "air")
                palette.append(arr)

            palette_len = 1

            for chunk in self._chunks.values():
                if chunk.selection.intersects(selection):
                    box = chunk.selection.create_moved_box(selection.min, subtract=True)
                    blocks[box.slice] = chunk.blocks + palette_len
                    palette.append(chunk.palette)
                    palette_len += len(chunk.palette)
                    for be in chunk.block_entities:
                        be = copy.deepcopy(be)
                        be["Pos"] = IntArrayTag(be["Pos"].np_array - selection.min)
                        block_entities.append(be)

                    for e in chunk.entities:
                        e = copy.deepcopy(e)
                        x, y, z = e["Pos"]
                        e["Pos"] = ListTag(
                            [
                                IntTag(x - selection.min_x),
                                IntTag(y - selection.min_y),
                                IntTag(z - selection.min_z),
                            ]
                        )
                        entities.append(e)

            compact_palette, lut = brute_sort_objects_no_hash(
                numpy.concatenate(palette)
            )
            blocks = numpy.transpose(lut[blocks], (1, 2, 0)).ravel()  # XYZ => YZX
            block_palette = []
            for index, block in enumerate(compact_palette):
                block: Block
                block_palette.append(block.blockstate)

            tag["PaletteMax"] = IntTag(len(compact_palette))
            tag["Palette"] = CompoundTag(
                {
                    blockstate: IntTag(index)
                    for index, blockstate in enumerate(block_palette)
                }
            )
            tag["BlockData"] = ByteArrayTag(list(encode_array(blocks)))
            if block_entities:
                tag["BlockEntities"] = ListTag(block_entities)
            if entities:
                tag["Entities"] = ListTag(entities)

            NamedTag(tag, "Schematic").save_to(f)
        else:
            raise SpongeSchemReadError(
                f"Sponge Schematic Version {self._schem_version} is not supported currently."
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
        interface: SpongeSchemInterface,
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
        section: SpongeSchemChunk,
        dimension: Optional[Dimension] = None,
    ):
        self._chunks[(cx, cz)] = copy.deepcopy(section)

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: Optional[Dimension] = None
    ) -> SpongeSchemChunk:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        if (cx, cz) in self._chunks:
            return copy.deepcopy(self._chunks[(cx, cz)])
        else:
            raise ChunkDoesNotExist

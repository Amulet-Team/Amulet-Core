import os
from typing import Optional, List, Tuple, Dict, Generator, TYPE_CHECKING, BinaryIO
import numpy
from io import BytesIO
import struct

import amulet_nbt

from amulet import log
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    Dimension,
    PlatformType)
from amulet.api.registry import BlockManager
from amulet.api.wrapper import StructureFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ChunkDoesNotExist

from .section import ConstructionSection
from .interface import Construction0Interface, ConstructionInterface
from .util import unpack_palette, parse_entities, parse_block_entities, serialise_entities, serialise_block_entities, find_fitting_array_type, pack_palette

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface

construction_0_interface = Construction0Interface()

INT_STRUCT = struct.Struct(">I")
SECTION_ENTRY_TYPE = numpy.dtype(
    [
        ("sx", "i4"),
        ("sy", "i4"),
        ("sz", "i4"),
        ("shapex", "i1"),
        ("shapey", "i1"),
        ("shapez", "i1"),
        ("position", "i4"),
        ("length", "i4"),
    ]
)

magic_num = b"constrct"
magic_num_len = len(magic_num)

max_format_version = 0
max_section_version = 0


class ConstructionFormatWrapper(StructureFormatWrapper):
    def __init__(self, path: str):
        super().__init__(path)

        self._format_version: int = max_format_version
        self._section_version: int = max_section_version

        # which sections are in a given chunk
        self._chunk_to_section: Dict[Tuple[int, int], List[ConstructionSection]] = {}

        self._selection_boxes: List[SelectionBox] = []

        # which selection boxes intersect a given chunk (boxes are clipped to the size of the chunk)
        self._chunk_to_box: Dict[Tuple[int, int], List[SelectionBox]] = {}

    def _create(self, format_version=max_format_version, section_version=max_section_version, **kwargs):
        self._format_version = format_version
        self._section_version = section_version
        self._chunk_to_section = {}
        self._chunk_to_box = {}
        self._populate_chunk_to_box()

    def _populate_chunk_to_box(self):
        for box in self._selection.selection_boxes:
            for cx, cz in box.chunk_locations():
                self._chunk_to_box.setdefault(
                    (cx, cz),
                    []
                ).append(
                    SelectionBox.create_chunk_box(cx, cz).intersection(box)
                )

    def open_from(self, f: BinaryIO):
        f = BytesIO(f.read())
        magic_num_1 = f.read(8)
        assert magic_num_1 == magic_num, f"This file is not a construction file."
        self._format_version = struct.unpack(">B", f.read(1))[0]
        if self._format_version == 0:
            f.seek(-magic_num_len, os.SEEK_END)
            magic_num_2 = f.read(8)
            assert (
                    magic_num_2 == magic_num
            ), "It looks like this file is corrupt. It probably wasn't saved properly"

            f.seek(-magic_num_len - INT_STRUCT.size, os.SEEK_END)
            metadata_end = f.tell()
            metadata_start = INT_STRUCT.unpack(f.read(INT_STRUCT.size))[0]
            f.seek(metadata_start)

            metadata = amulet_nbt.load(
                f.read(metadata_end - metadata_start),
                compressed=True,
            )

            try:
                self._platform = metadata["export_version"]["edition"].value
                self._version = tuple(
                    map(lambda v: v.value, metadata["export_version"]["version"])
                )
            except KeyError as e:
                raise KeyError(
                    f'Missing export version identifying key "{e.args[0]}"'
                )

            self._section_version = metadata["section_version"].value

            palette = unpack_palette(metadata["block_palette"])

            selection_boxes = (
                metadata["selection_boxes"].value.reshape(-1, 6).tolist()
            )

            self._selection = SelectionGroup([
                SelectionBox((minx, miny, minz), (maxx, maxy, maxz))
                for minx, miny, minz, maxx, maxy, maxz in selection_boxes
            ])

            self._populate_chunk_to_box()

            section_index_table = (
                metadata["section_index_table"].value.view(SECTION_ENTRY_TYPE).tolist()
            )

            if self._section_version == 0:
                for (
                    start_x,
                    start_y,
                    start_z,
                    shape_x,
                    shape_y,
                    shape_z,
                    position,
                    length,
                ) in section_index_table:
                    f.seek(position)
                    nbt_obj = amulet_nbt.load(f.read(length))
                    if nbt_obj["blocks_array_type"].value == -1:
                        blocks = None
                        block_entities = None
                    else:
                        blocks = numpy.reshape(
                            nbt_obj["blocks"].value, (shape_x, shape_y, shape_z)
                        )
                        block_entities = parse_block_entities(nbt_obj["block_entities"])

                    start = numpy.array([start_x, start_y, start_z])
                    chunk_index: numpy.ndarray = start // self.sub_chunk_size
                    shape = numpy.array([shape_x, shape_y, shape_z])
                    if numpy.any(shape <= 0):
                        continue  # skip sections with zero size
                    if numpy.any(start + shape > (chunk_index + 1) * self.sub_chunk_size):
                        log.error(f"section in construction file did not fit in one sub-chunk. Start: {start}, Shape: {shape}")
                    cx, cy, cz = chunk_index.tolist()
                    self._chunk_to_section.setdefault((cx, cz), []).append(
                        ConstructionSection(
                            (start_x, start_y, start_z),
                            (shape_x, shape_y, shape_z),
                            blocks,
                            palette,
                            parse_entities(nbt_obj["entities"]),
                            block_entities,
                        )
                    )
            else:
                raise Exception(
                    f"This wrapper does not support any construction section version higher than {max_section_version}"
                )

        else:
            raise Exception(
                f"This wrapper does not support any construction format version higher than {max_format_version}"
            )

    @property
    def multi_selection(self) -> bool:
        return True

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        Returns whether this format is able to load the given object.

        :param path: The path of the object to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        return os.path.isfile(path) and path.endswith(".construction")

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {
            "bedrock": (True, True),
            "java": (True, True),
        }

    @property
    def extensions(self) -> Tuple[str, ...]:
        return ".construction",

    def _get_interface(
        self, max_world_version, raw_chunk_data=None
    ) -> "ConstructionInterface":
        return construction_0_interface

    def _get_interface_and_translator(
        self, max_world_version, raw_chunk_data=None
    ) -> Tuple["Interface", "Translator", VersionNumberAny]:
        interface = self._get_interface(max_world_version, raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            max_world_version, raw_chunk_data, self.translation_manager
        )
        return interface, translator, version_identifier

    def save_to(self, f: BinaryIO):
        palette: BlockManager = BlockManager()
        f.write(magic_num)
        f.write(struct.pack(">B", self._format_version))
        if self._format_version == 0:
            metadata = amulet_nbt.NBTFile(
                amulet_nbt.TAG_Compound(
                    {
                        "created_with": amulet_nbt.TAG_String("amulet_python_wrapper_v2"),
                        "selection_boxes": amulet_nbt.TAG_Int_Array(
                            [
                                c for box in self._selection.selection_boxes for c in (*box.min, *box.max)
                            ]
                        ),
                        "section_version": amulet_nbt.TAG_Byte(self._section_version),
                        "export_version": amulet_nbt.TAG_Compound(
                            {
                                "edition": amulet_nbt.TAG_String(self._platform),
                                "version": amulet_nbt.TAG_List(
                                    [
                                        amulet_nbt.TAG_Int(v)
                                        for v in self._version
                                    ]
                                ),
                            }
                        ),
                    }
                )
            )
            section_index_table: List[
                Tuple[int, int, int, int, int, int, int, int]
            ] = []
            if self._section_version == 0:
                for section_list in self._chunk_to_section.values():
                    for section in section_list:
                        sx, sy, sz = section.location
                        shapex, shapey, shapez = section.shape
                        blocks = section.blocks
                        entities = section.entities
                        block_entities = section.block_entities
                        palette = section.palette
                        position = f.tell()

                        _tag = amulet_nbt.TAG_Compound(
                            {"entities": serialise_entities(entities)}
                        )

                        if blocks is None:
                            _tag["blocks_array_type"] = amulet_nbt.TAG_Byte(-1)
                        else:
                            flattened_array = blocks.ravel()
                            index, flattened_array = numpy.unique(
                                flattened_array, return_inverse=True
                            )
                            palette = numpy.array(palette, dtype=object)[index]
                            lut = numpy.vectorize(palette.get_add_block)(palette)
                            flattened_array = lut[flattened_array]
                            array_type = find_fitting_array_type(flattened_array)
                            _tag["blocks_array_type"] = amulet_nbt.TAG_Byte(array_type().tag_id)
                            _tag["blocks"] = array_type(flattened_array)
                            _tag["block_entities"] = serialise_block_entities(
                                block_entities or []
                            )

                        amulet_nbt.NBTFile(_tag).save_to(f)

                        length = f.tell() - position
                        section_index_table.append(
                            (sx, sy, sz, shapex, shapey, shapez, position, length)
                        )
            else:
                raise Exception(
                    f"This wrapper doesn't support any section version higher than {max_section_version}"
                )
            metadata_start = f.tell()
            metadata["section_index_table"] = amulet_nbt.TAG_Byte_Array(
                numpy.array(section_index_table, dtype=SECTION_ENTRY_TYPE).view(
                    numpy.int8
                )
            )
            metadata["block_palette"] = pack_palette(palette)
            metadata.save_to(f)
            f.write(INT_STRUCT.pack(metadata_start))
            f.write(magic_num)
        else:
            raise Exception(
                f"This wrapper doesn't support any construction version higher than {max_format_version}"
            )

    def _close(self):
        """Close the disk database"""
        pass

    def unload(self):
        """Unload data stored in the Format class"""
        pass

    def all_chunk_coords(
        self, dimension: Optional[Dimension] = None
    ) -> Generator[Tuple[int, int], None, None]:
        """A generator of all chunk coords"""
        yield from self._chunk_to_section.keys()

    def _pack(
        self, chunk: "Chunk", translator: "Translator", chunk_version: VersionNumberAny,
    ) -> Tuple["Chunk", AnyNDArray]:
        return chunk, numpy.array(chunk.block_palette.blocks())

    def _encode(
        self, chunk: Chunk, chunk_palette: AnyNDArray, interface: ConstructionInterface,
    ):
        return interface.encode(
            chunk,
            chunk_palette,
            self.max_world_version,
            self._chunk_to_box.get((chunk.cx, chunk.cz)),
        )

    def _unpack(
        self,
        translator: "Translator",
        game_version: VersionNumberAny,
        chunk: "Chunk",
        chunk_palette: AnyNDArray,
    ) -> "Chunk":
        palette = chunk._block_palette = BlockManager()
        lut = numpy.array([palette.get_add_block(block) for block in chunk_palette])
        if len(palette.blocks()) != len(chunk_palette):
            # if a blockstate was defined twice
            for cy in chunk.blocks.sub_chunks:
                chunk.blocks.add_sub_chunk(cy, lut[chunk.blocks.get_sub_chunk(cy)])
        return chunk

    def _delete_chunk(self, cx: int, cz: int, dimension: Optional[Dimension] = None):
        if (cx, cz) in self._chunk_to_section:
            del self._chunk_to_section[(cx, cz)]

    def _put_raw_chunk_data(
        self,
        cx: int,
        cz: int,
        data: List[ConstructionSection],
        dimension: Optional[Dimension] = None,
    ):
        """
        Actually stores the data from the interface to disk.
        """
        self._chunk_to_section[cx, cz] = data

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: Optional[Dimension] = None
    ) -> List[ConstructionSection]:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        if (cx, cz) in self._chunk_to_section:
            return self._chunk_to_section[(cx, cz)].copy()
        else:
            raise ChunkDoesNotExist

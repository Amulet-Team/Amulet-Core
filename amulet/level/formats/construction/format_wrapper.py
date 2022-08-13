import os
from typing import (
    Optional,
    List,
    Tuple,
    Dict,
    Iterable,
    TYPE_CHECKING,
    BinaryIO,
    Any,
    Union,
)
import numpy
from io import BytesIO
import struct
import copy
import logging

from amulet_nbt import (
    ByteTag,
    IntTag,
    StringTag,
    ListTag,
    CompoundTag,
    ByteArrayTag,
    IntArrayTag,
    NamedTag,
    load as load_nbt,
)


from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    VersionNumberTuple,
    Dimension,
    PlatformType,
    ChunkCoordinates,
)
from amulet.api.registry import BlockManager
from amulet.api.wrapper import StructureFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ChunkDoesNotExist, ObjectWriteError

from .section import ConstructionSection
from .interface import Construction0Interface, ConstructionInterface
from .util import (
    unpack_palette,
    parse_entities,
    parse_block_entities,
    serialise_entities,
    serialise_block_entities,
    find_fitting_array_type,
    pack_palette,
)

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface

log = logging.getLogger(__name__)

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


class ConstructionFormatWrapper(StructureFormatWrapper[VersionNumberTuple]):
    """
    This FormatWrapper class exists to interface with the construction format.
    """

    _format_version: int
    _section_version: int
    _chunk_to_section: Dict[Tuple[int, int], List[ConstructionSection]]
    _selection_boxes: List[SelectionBox]
    _chunk_to_box: Dict[Tuple[int, int], List[SelectionBox]]

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`ConstructionFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)

        self._format_version = max_format_version
        self._section_version = max_section_version

        # which sections are in a given chunk
        self._chunk_to_section = {}

        self._selection_boxes = []

        # which selection boxes intersect a given chunk (boxes are clipped to the size of the chunk)
        self._chunk_to_box = {}

        self._shallow_load()

    def _shallow_load(self):
        if os.path.isfile(self.path):
            with open(self.path, "rb") as f:
                magic_num_1 = f.read(magic_num_len)
                if magic_num_1 == magic_num:
                    format_version = struct.unpack(">B", f.read(1))[0]
                    if format_version == 0:
                        f.seek(-magic_num_len, os.SEEK_END)
                        magic_num_2 = f.read(magic_num_len)
                        if magic_num_2 == magic_num:
                            f.seek(-magic_num_len - INT_STRUCT.size, os.SEEK_END)
                            metadata_end = f.tell()
                            metadata_start = INT_STRUCT.unpack(f.read(INT_STRUCT.size))[
                                0
                            ]
                            f.seek(metadata_start)

                            metadata = load_nbt(
                                f.read(metadata_end - metadata_start),
                                compressed=True,
                            ).compound

                            export_version = metadata.get_compound("export_version")

                            self._platform = export_version.get_string("edition").py_str
                            self._version = tuple(
                                map(
                                    lambda v: v.py_int,
                                    export_version.get_list("version"),
                                )
                            )

                            selection_boxes = (
                                metadata.get_int_array("selection_boxes")
                                .np_array.reshape(-1, 6)
                                .tolist()
                            )
                            self._bounds[self.dimensions[0]] = SelectionGroup(
                                [
                                    SelectionBox((minx, miny, minz), (maxx, maxy, maxz))
                                    for minx, miny, minz, maxx, maxy, maxz in selection_boxes
                                ]
                            )

    def _create(
        self,
        overwrite: bool,
        bounds: Union[
            SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None
        ] = None,
        format_version=max_format_version,
        section_version=max_section_version,
        **kwargs,
    ):
        if not overwrite and os.path.isfile(self.path):
            raise ObjectWriteError(f"There is already a file at {self.path}")
        self._format_version = format_version
        self._section_version = section_version
        translator_version = self.translation_manager.get_version(
            self.platform, self.version
        )
        self._platform = translator_version.platform
        self._version = translator_version.version_number
        self._chunk_to_section = {}
        self._chunk_to_box = {}
        self._set_selection(bounds)
        self._populate_chunk_to_box()
        self._is_open = True
        self._has_lock = True

    def _populate_chunk_to_box(self):
        for box in self._bounds[self.dimensions[0]].selection_boxes:
            for cx, cz in box.chunk_locations():
                self._chunk_to_box.setdefault((cx, cz), []).append(
                    SelectionBox.create_chunk_box(cx, cz).intersection(box)
                )

    def open_from(self, f: BinaryIO):
        f = BytesIO(f.read())
        magic_num_1 = f.read(magic_num_len)
        assert magic_num_1 == magic_num, f"This file is not a construction file."
        self._format_version = struct.unpack(">B", f.read(1))[0]
        if self._format_version == 0:
            f.seek(-magic_num_len, os.SEEK_END)
            magic_num_2 = f.read(magic_num_len)
            assert (
                magic_num_2 == magic_num
            ), "It looks like this file is corrupt. It probably wasn't saved properly"

            f.seek(-magic_num_len - INT_STRUCT.size, os.SEEK_END)
            metadata_end = f.tell()
            metadata_start = INT_STRUCT.unpack(f.read(INT_STRUCT.size))[0]
            f.seek(metadata_start)

            metadata = load_nbt(
                f.read(metadata_end - metadata_start),
                compressed=True,
            ).compound

            try:
                export_version = metadata.get_compound("export_version")
                self._platform = export_version.get_string("edition").py_str
                self._version = tuple(
                    map(lambda v: v.py_int, export_version.get_list("version"))
                )
            except KeyError as e:
                raise KeyError(f'Missing export version identifying key "{e.args[0]}"')

            self._section_version = metadata.get_byte("section_version").py_int

            palette = unpack_palette(metadata.get_list("block_palette"))

            selection_boxes = (
                metadata.get_int_array("selection_boxes")
                .np_array.reshape(-1, 6)
                .tolist()
            )

            self._bounds[self.dimensions[0]] = SelectionGroup(
                [
                    SelectionBox((minx, miny, minz), (maxx, maxy, maxz))
                    for minx, miny, minz, maxx, maxy, maxz in selection_boxes
                ]
            )

            self._populate_chunk_to_box()

            section_index_table = (
                metadata.get_byte_array("section_index_table")
                .np_array.view(SECTION_ENTRY_TYPE)
                .tolist()
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
                    nbt_obj = load_nbt(f.read(length)).compound
                    blocks_array_type = nbt_obj.get_byte("blocks_array_type").py_int
                    if blocks_array_type == -1:
                        blocks = None
                        block_entities = None
                    else:
                        if blocks_array_type == 7:
                            block_array = nbt_obj.get_byte_array("blocks").np_array
                        elif blocks_array_type == 11:
                            block_array = nbt_obj.get_int_array("blocks").np_array
                        elif blocks_array_type == 12:
                            block_array = nbt_obj.get_long_array("blocks").np_array
                        else:
                            raise TypeError

                        blocks = block_array.reshape((shape_x, shape_y, shape_z))
                        block_entities = parse_block_entities(
                            nbt_obj.get_list("block_entities")
                        )

                    start = numpy.array([start_x, start_y, start_z])
                    chunk_index: numpy.ndarray = start // self.sub_chunk_size
                    shape = numpy.array([shape_x, shape_y, shape_z])
                    if numpy.any(shape <= 0):
                        continue  # skip sections with zero size
                    if numpy.any(
                        start + shape > (chunk_index + 1) * self.sub_chunk_size
                    ):
                        log.error(
                            f"section in construction file did not fit in one sub-chunk. Start: {start}, Shape: {shape}"
                        )
                    cx, cy, cz = chunk_index.tolist()
                    self._chunk_to_section.setdefault((cx, cz), []).append(
                        ConstructionSection(
                            (start_x, start_y, start_z),
                            (shape_x, shape_y, shape_z),
                            blocks,
                            palette,
                            parse_entities(nbt_obj.get_list("entities")),
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
        return os.path.isfile(path) and path.endswith(".construction")

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {
            "bedrock": (True, True),
            "java": (True, True),
        }

    @property
    def extensions(self) -> Tuple[str, ...]:
        return (".construction",)

    def _get_interface(
        self, raw_chunk_data: Optional[Any] = None
    ) -> Construction0Interface:
        return construction_0_interface

    def _get_interface_and_translator(
        self, raw_chunk_data=None
    ) -> Tuple["Interface", "Translator", VersionNumberAny]:
        interface = self._get_interface(raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            self.max_world_version, raw_chunk_data, self.translation_manager
        )
        return interface, translator, version_identifier

    def save_to(self, f: BinaryIO):
        palette: BlockManager = BlockManager()
        f.write(magic_num)
        f.write(struct.pack(">B", self._format_version))
        if self._format_version == 0:
            metadata = CompoundTag(
                {
                    "created_with": StringTag("amulet_python_wrapper_v2"),
                    "selection_boxes": IntArrayTag(
                        [
                            c
                            for box in self._bounds[self.dimensions[0]].selection_boxes
                            for c in (*box.min, *box.max)
                        ]
                    ),
                    "section_version": ByteTag(self._section_version),
                    "export_version": CompoundTag(
                        {
                            "edition": StringTag(self._platform),
                            "version": ListTag([IntTag(v) for v in self._version]),
                        }
                    ),
                }
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
                        section_palette = section.palette
                        position = f.tell()

                        _tag = CompoundTag({"entities": serialise_entities(entities)})

                        if blocks is None:
                            _tag["blocks_array_type"] = ByteTag(-1)
                        else:
                            flattened_array = blocks.ravel()
                            index, flattened_array = numpy.unique(
                                flattened_array, return_inverse=True
                            )
                            section_palette = numpy.array(
                                section_palette, dtype=object
                            )[index]
                            lut = numpy.vectorize(palette.get_add_block)(
                                section_palette
                            )
                            flattened_array = lut[flattened_array]
                            array_type = find_fitting_array_type(flattened_array)
                            _tag["blocks_array_type"] = ByteTag(array_type.tag_id)
                            _tag["blocks"] = array_type(flattened_array)
                            _tag["block_entities"] = serialise_block_entities(
                                block_entities or []
                            )

                        NamedTag(_tag).save_to(f)

                        length = f.tell() - position
                        section_index_table.append(
                            (sx, sy, sz, shapex, shapey, shapez, position, length)
                        )
            else:
                raise Exception(
                    f"This wrapper doesn't support any section version higher than {max_section_version}"
                )
            metadata_start = f.tell()
            metadata["section_index_table"] = ByteArrayTag(
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
        pass

    def all_chunk_coords(
        self, dimension: Optional[Dimension] = None
    ) -> Iterable[ChunkCoordinates]:
        yield from self._chunk_to_section.keys()

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return (cx, cz) in self._chunk_to_section

    def _pack(
        self,
        chunk: "Chunk",
        translator: "Translator",
        chunk_version: VersionNumberAny,
    ) -> Tuple["Chunk", AnyNDArray]:
        return chunk, numpy.array(chunk.block_palette.blocks)

    def _encode(
        self,
        interface: ConstructionInterface,
        chunk: Chunk,
        dimension: Dimension,
        chunk_palette: AnyNDArray,
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
        if len(palette.blocks) != len(chunk_palette):
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
        self._chunk_to_section[cx, cz] = copy.deepcopy(data)

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
            return copy.deepcopy(self._chunk_to_section[(cx, cz)])
        else:
            raise ChunkDoesNotExist

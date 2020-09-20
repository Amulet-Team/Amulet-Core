from __future__ import annotations

import os
import struct
from typing import Type, Union, Tuple, IO, List, Optional

from amulet import Block
from amulet.api.registry import BlockManager
from amulet.api.entity import Entity
from amulet.api.block_entity import BlockEntity

import amulet_nbt

import numpy

INT_TRIPLET = Tuple[int, int, int]

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


class ConstructionSection:
    __slots__ = (
        "sx",
        "sy",
        "sz",
        "blocks",
        "palette",
        "shape",
        "entities",
        "block_entities",
    )

    def __init__(
        self,
        min_position: INT_TRIPLET,
        shape: INT_TRIPLET,
        blocks: Optional[numpy.ndarray],
        palette: List[Block],
        entities: List[Entity],
        block_entities: List[BlockEntity],
    ):
        self.sx, self.sy, self.sz = min_position
        self.shape = shape
        self.blocks = blocks
        if blocks is not None:
            assert isinstance(self.blocks, numpy.ndarray)
            assert (
                self.shape == self.blocks.shape
            ), "blocks shape does not match the specified section shape"
        self.palette = palette
        self.entities = entities
        self.block_entities = block_entities

    def __eq__(self, other):
        return (
            isinstance(other, ConstructionSection)
            and self.sx == other.sx
            and self.sy == other.sy
            and self.sz == other.sz
            and self.shape == other.shape
            and numpy.equal(self.blocks, other.blocks).all()
            and self.entities == other.entities
            and self.block_entities == other.block_entities
        )

    @property
    def location(self) -> Tuple[int, int, int]:
        return self.sx, self.sy, self.sz


class ConstructionReader:
    def __init__(self, file_or_buffer: Union[str, IO]):
        self._format_version: Optional[int] = None
        self._section_version: Optional[int] = None

        if isinstance(file_or_buffer, str):
            assert os.path.isfile(
                file_or_buffer
            ), f"There is no file located at {file_or_buffer}"
            self._buffer = open(file_or_buffer, "rb")
        else:
            assert hasattr(
                file_or_buffer, "read"
            ), "Construction file buffer does not have a read mode"
            self._buffer = file_or_buffer

        self._source_edition: Optional[str] = None
        self._source_version: Optional[INT_TRIPLET] = None

        self._selection_boxes: Optional[
            List[Tuple[int, int, int, int, int, int]]
        ] = None

        self._metadata: Optional[amulet_nbt.NBTFile] = None
        self._section_index_table: Optional[
            List[Tuple[int, int, int, int, int, int, int, int]]
        ] = None
        self._palette: Optional[List[Block]] = None
        self._init_read()

    @property
    def metadata(self) -> amulet_nbt.NBTFile:
        return self._metadata

    @property
    def palette(self) -> List[Block]:
        return self._palette.copy()

    @property
    def sections(self) -> List[Tuple[int, int, int, int, int, int, int, int]]:
        return self._section_index_table.copy()

    @property
    def source_edition(self) -> str:
        return self._source_edition

    @property
    def source_version(self) -> INT_TRIPLET:
        return self._source_version

    @property
    def selection(self) -> List[Tuple[int, int, int, int, int, int]]:
        return self._selection_boxes.copy()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def _unpack_palette(raw_palette: amulet_nbt.TAG_List) -> List[Block]:
        block_palette = []
        extra_block_map = {}
        for block_index, block_nbt in enumerate(raw_palette):
            block_nbt: amulet_nbt.TAG_Compound
            block_namespace = block_nbt["namespace"].value
            block_basename = block_nbt["blockname"].value
            block = Block(
                namespace=block_namespace,
                base_name=block_basename,
                properties=block_nbt["properties"].value,
            )

            if block_nbt["extra_blocks"].value:
                extra_block_map[block_index] = block_nbt["extra_blocks"].value

            block_palette.append(block)

        for block_index, extra_blocks in extra_block_map.items():
            extra_block_objects = [block_palette[i.value] for i in extra_blocks]

            resulting_block = block_palette[block_index]
            for extra_block in extra_block_objects:
                resulting_block = resulting_block + extra_block

            block_palette[block_index] = resulting_block
        return block_palette

    def _init_read(self):
        """data to be read at init in read mode"""
        magic_num_1 = self._buffer.read(8)
        assert magic_num_1 == magic_num, f"This file is not a construction file."
        self._format_version = struct.unpack(">B", self._buffer.read(1))[0]
        if self._format_version == 0:
            self._buffer.seek(-magic_num_len, os.SEEK_END)
            magic_num_2 = self._buffer.read(8)
            assert (
                magic_num_2 == magic_num
            ), "It looks like this file is corrupt. It probably wasn't saved properly"

            self._buffer.seek(-magic_num_len - INT_STRUCT.size, os.SEEK_END)
            metadata_end = self._buffer.tell()
            metadata_start = INT_STRUCT.unpack(self._buffer.read(INT_STRUCT.size))[0]
            self._buffer.seek(metadata_start)

            metadata = amulet_nbt.load(
                buffer=self._buffer.read(metadata_end - metadata_start),
                compressed=True,
            )

            try:
                self._source_edition = metadata["export_version"]["edition"].value
                self._source_version = tuple(
                    map(lambda v: v.value, metadata["export_version"]["version"])
                )
            except KeyError as e:
                raise AssertionError(
                    f'Missing export version identifying key "{e.args[0]}"'
                )

            self._section_version = metadata["section_version"].value

            self._palette = self._unpack_palette(metadata["block_palette"])

            self._selection_boxes = (
                metadata["selection_boxes"].value.reshape(-1, 6).tolist()
            )

            self._section_index_table = (
                metadata["section_index_table"].value.view(SECTION_ENTRY_TYPE).tolist()
            )

        else:
            raise Exception(
                f"This wrapper doesn't support any construction version higher than {max_format_version}"
            )

    @staticmethod
    def _parse_entities(entities: amulet_nbt.TAG_List) -> List[Entity]:
        return [
            Entity(
                entity["namespace"].value,
                entity["base_name"].value,
                entity["x"].value,
                entity["y"].value,
                entity["z"].value,
                amulet_nbt.NBTFile(entity["nbt"]),
            )
            for entity in entities
        ]

    @staticmethod
    def _parse_block_entities(block_entities: amulet_nbt.TAG_List) -> List[BlockEntity]:
        return [
            BlockEntity(
                block_entity["namespace"].value,
                block_entity["base_name"].value,
                block_entity["x"].value,
                block_entity["y"].value,
                block_entity["z"].value,
                amulet_nbt.NBTFile(block_entity["nbt"]),
            )
            for block_entity in block_entities
        ]

    def read(self, section_index: int):
        if self._format_version == 0:
            (
                sx,
                sy,
                sz,
                shapex,
                shapey,
                shapez,
                position,
                length,
            ) = self._section_index_table[section_index]
            self._buffer.seek(position)
            nbt_obj = amulet_nbt.load(buffer=self._buffer.read(length))
            if nbt_obj["blocks_array_type"].value == -1:
                blocks = None
                block_entities = None
            else:
                blocks = numpy.reshape(
                    nbt_obj["blocks"].value, (shapex, shapey, shapez)
                )
                block_entities = self._parse_block_entities(nbt_obj["block_entities"])

            return ConstructionSection(
                (sx, sy, sz),
                (shapex, shapey, shapez),
                blocks,
                self._palette,
                self._parse_entities(nbt_obj["entities"]),
                block_entities,
            )
        else:
            raise Exception(
                f"This wrapper doesn't support any construction version higher than {max_format_version}"
            )

    def close(self):
        self._buffer.close()


class ConstructionWriter:
    def __init__(
        self,
        file_or_buffer: Union[str, IO],
        source_edition: str,
        source_version: INT_TRIPLET,
        selection_boxes: Optional[List[Tuple[int, int, int, int, int, int]]] = None,
        format_version: int = max_format_version,
        section_version: int = max_section_version,
    ):
        assert (
            format_version <= max_format_version
        ), f"This construction writer does not support format versions above {max_format_version}"
        assert (
            section_version <= max_section_version
        ), f"This construction writer does not support section versions above {max_section_version}"
        self._format_version = format_version
        self._section_version = section_version

        if isinstance(file_or_buffer, str):
            self._buffer = open(file_or_buffer, "wb")
        else:
            assert hasattr(
                file_or_buffer, "write"
            ), "Construction file buffer does not have a write mode"
            self._buffer = file_or_buffer

        self._source_edition = source_edition
        self._source_version = source_version

        self._selection_boxes = selection_boxes or []

        self._metadata: Optional[amulet_nbt.NBTFile] = None
        self._section_index_table: List[
            Tuple[int, int, int, int, int, int, int, int]
        ] = []
        self._palette: BlockManager = BlockManager()
        self._init_write()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _init_write(self):
        """data to be written at init in write mode"""
        self._buffer.write(magic_num)
        self._buffer.write(struct.pack(">B", self._format_version))
        if self._format_version == 0:
            self._metadata = amulet_nbt.NBTFile(
                amulet_nbt.TAG_Compound(
                    {
                        "created_with": amulet_nbt.TAG_String("amulet_python_wrapper"),
                        "selection_boxes": amulet_nbt.TAG_Int_Array(
                            [
                                c
                                for box in self._selection_boxes
                                if len(box) == 6
                                and all(isinstance(c, int) for c in box)
                                for c in box
                            ]
                        ),
                        "section_version": amulet_nbt.TAG_Byte(self._section_version),
                        "export_version": amulet_nbt.TAG_Compound(
                            {
                                "edition": amulet_nbt.TAG_String(self._source_edition),
                                "version": amulet_nbt.TAG_List(
                                    [
                                        amulet_nbt.TAG_Int(v)
                                        for v in self._source_version
                                    ]
                                ),
                            }
                        ),
                    }
                )
            )
        else:
            raise Exception(
                f"This wrapper doesn't support any construction version higher than {max_format_version}"
            )

    @staticmethod
    def _generate_block_entry(
        _block: Block, _palette_len, _extra_blocks
    ) -> amulet_nbt.TAG_Compound:
        return amulet_nbt.TAG_Compound(
            {
                "namespace": amulet_nbt.TAG_String(_block.namespace),
                "blockname": amulet_nbt.TAG_String(_block.base_name),
                "properties": amulet_nbt.TAG_Compound(_block.properties),
                "extra_blocks": amulet_nbt.TAG_List(
                    [
                        amulet_nbt.TAG_Int(
                            _palette_len + _extra_blocks.index(_extra_block)
                        )
                        for _extra_block in _block.extra_blocks
                    ]
                ),
            }
        )

    @staticmethod
    def _serialise_entities(entities: List[Entity]) -> amulet_nbt.TAG_List:
        return amulet_nbt.TAG_List(
            [
                amulet_nbt.TAG_Compound(
                    {
                        "namespace": amulet_nbt.TAG_String(entity.namespace),
                        "base_name": amulet_nbt.TAG_String(entity.base_name),
                        "x": amulet_nbt.TAG_Double(entity.x),
                        "y": amulet_nbt.TAG_Double(entity.y),
                        "z": amulet_nbt.TAG_Double(entity.z),
                        "nbt": entity.nbt.value,
                    }
                )
                for entity in entities
            ]
        )

    @staticmethod
    def _serialise_block_entities(
        block_entities: List[BlockEntity],
    ) -> amulet_nbt.TAG_List:
        return amulet_nbt.TAG_List(
            [
                amulet_nbt.TAG_Compound(
                    {
                        "namespace": amulet_nbt.TAG_String(block_entity.namespace),
                        "base_name": amulet_nbt.TAG_String(block_entity.base_name),
                        "x": amulet_nbt.TAG_Int(block_entity.x),
                        "y": amulet_nbt.TAG_Int(block_entity.y),
                        "z": amulet_nbt.TAG_Int(block_entity.z),
                        "nbt": block_entity.nbt.value,
                    }
                )
                for block_entity in block_entities
            ]
        )

    def _pack_palette(self) -> amulet_nbt.TAG_List:
        block_palette_nbt = amulet_nbt.TAG_List()
        extra_blocks = set()

        for block in self._palette.blocks():
            if len(block.extra_blocks) > 0:
                extra_blocks.update(block.extra_blocks)

        extra_blocks = list(extra_blocks)

        palette_len = len(self._palette)
        for block_entry in self._palette.blocks():
            block_palette_nbt.append(
                self._generate_block_entry(block_entry, palette_len, extra_blocks)
            )

        for extra_block in extra_blocks:
            block_palette_nbt.append(
                self._generate_block_entry(extra_block, palette_len, extra_blocks)
            )
        return block_palette_nbt

    def _exit_write(self):
        """data to be written at close in write mode"""
        if self._format_version == 0:
            metadata_start = self._buffer.tell()
            self._metadata["section_index_table"] = amulet_nbt.TAG_Byte_Array(
                numpy.array(self._section_index_table, dtype=SECTION_ENTRY_TYPE).view(
                    numpy.int8
                )
            )
            self._metadata["block_palette"] = self._pack_palette()
            self._metadata.save_to(self._buffer)
            self._buffer.write(INT_STRUCT.pack(metadata_start))
            self._buffer.write(magic_num)
        else:
            raise Exception(
                f"This wrapper doesn't support any construction version higher than {max_format_version}"
            )
        self._buffer.close()

    @staticmethod
    def _find_fitting_array_type(
        array: numpy.ndarray,
    ) -> Type[
        Union[
            amulet_nbt.TAG_Int_Array,
            amulet_nbt.TAG_Byte_Array,
            amulet_nbt.TAG_Long_Array,
        ]
    ]:
        max_element = array.max(initial=0)

        if max_element <= 127:
            return amulet_nbt.TAG_Byte_Array
        elif max_element <= 2_147_483_647:
            return amulet_nbt.TAG_Int_Array
        else:
            return amulet_nbt.TAG_Long_Array

    def write(self, section: ConstructionSection):
        if self._section_version == 0:
            sx, sy, sz = section.location
            shapex, shapey, shapez = section.shape
            blocks = section.blocks
            entities = section.entities
            block_entities = section.block_entities
            palette = section.palette
            for point, shape in zip((sx, sy, sz), (shapex, shapey, shapez)):
                assert shape >= 0, "Shape must be positive"
                assert point + shape <= (
                    ((point >> 4) + 1) << 4
                ), "Section does not fit in a sub-chunk"
            position = self._buffer.tell()

            _tag = amulet_nbt.TAG_Compound(
                {"entities": self._serialise_entities(entities)}
            )

            if blocks is None:
                _tag["blocks_array_type"] = amulet_nbt.TAG_Byte(-1)
            else:
                flattened_array = blocks.ravel()
                index, flattened_array = numpy.unique(
                    flattened_array, return_inverse=True
                )
                palette = numpy.array(palette, dtype=object)[index]
                lut = numpy.vectorize(self._palette.get_add_block)(palette)
                flattened_array = lut[flattened_array]
                array_type = self._find_fitting_array_type(flattened_array)
                _tag["blocks_array_type"] = amulet_nbt.TAG_Byte(array_type().tag_id)
                _tag["blocks"] = array_type(flattened_array)
                _tag["block_entities"] = self._serialise_block_entities(
                    block_entities or []
                )

            amulet_nbt.NBTFile(_tag).save_to(self._buffer)

            length = self._buffer.tell() - position
            self._section_index_table.append(
                (sx, sy, sz, shapex, shapey, shapez, position, length)
            )
        else:
            raise Exception(
                f"This wrapper doesn't support any section version higher than {max_section_version}"
            )

    def close(self):
        self._exit_write()
        self._buffer.close()

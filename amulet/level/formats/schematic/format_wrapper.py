import os
from typing import Optional, Tuple, Iterable, TYPE_CHECKING, BinaryIO, Dict, Union
import numpy
import copy

import amulet_nbt

from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    Dimension,
    PlatformType,
    PointCoordinates,
    ChunkCoordinates,
)
from amulet.api.registry import BlockManager
from amulet.api.wrapper import StructureFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionBox, SelectionGroup
from amulet.api.errors import ObjectReadError, ObjectWriteError, ChunkDoesNotExist
from .interface import (
    JavaSchematicInterface,
    BedrockSchematicInterface,
    SchematicInterface,
)
from .data_types import BlockArrayType, BlockDataArrayType
from .chunk import SchematicChunk

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface

java_interface = JavaSchematicInterface()
bedrock_interface = BedrockSchematicInterface()


class SchematicFormatWrapper(StructureFormatWrapper):
    """
    This FormatWrapper class exists to interface with the legacy schematic structure format.
    """

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`SchematicFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)
        self._chunks: Dict[
            ChunkCoordinates,
            Tuple[SelectionBox, BlockArrayType, BlockDataArrayType, list, list],
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
        if self._platform == "bedrock":
            self._version = (1, 12, 0)
        else:
            self._platform = "java"
            self._version = (1, 12, 2)
        self._chunks = {}
        self._set_selection(bounds)
        self._is_open = True
        self._has_lock = True

    def open_from(self, f: BinaryIO):
        schematic = amulet_nbt.load(f)
        if "BlockData" in schematic:
            raise ObjectReadError("This file is not a legacy schematic file.")
        materials = schematic.get("Materials", amulet_nbt.TAG_String()).value
        if materials == "Alpha":
            self._platform = "java"
            self._version = (1, 12, 2)
        elif materials == "Pocket":
            self._platform = "bedrock"
            self._version = (1, 12, 0)
        else:
            raise Exception(
                f'"{materials}" is not a supported platform for a schematic file.'
            )
        self._chunks = {}
        selection_box = SelectionBox(
            (0, 0, 0),
            (
                schematic["Width"].value,
                schematic["Height"].value,
                schematic["Length"].value,
            ),
        )
        self._bounds[self.dimensions[0]] = SelectionGroup(selection_box)
        entities: amulet_nbt.TAG_List = schematic.get("Entities", amulet_nbt.TAG_List())
        block_entities: amulet_nbt.TAG_List = schematic.get(
            "TileEntities", amulet_nbt.TAG_List()
        )
        blocks: numpy.ndarray = (
            schematic["Blocks"].value.astype(numpy.uint8).astype(numpy.uint16)
        )
        if "AddBlocks" in schematic:
            add_blocks = schematic["AddBlocks"]
            blocks = (
                blocks
                + (
                    numpy.concatenate([[(add_blocks & 0xF0) >> 4], [add_blocks & 0xF]])
                    .T.ravel()
                    .astype(numpy.uint16)
                    << 8
                )[: blocks.size]
            )
        max_point = selection_box.max
        temp_shape = (max_point[1], max_point[2], max_point[0])
        blocks = numpy.transpose(blocks.reshape(temp_shape), (2, 0, 1))  # YZX => XYZ
        data = numpy.transpose(
            schematic["Data"].value.reshape(temp_shape), (2, 0, 1)
        ).astype(numpy.uint8)
        for cx, cz in selection_box.chunk_locations():
            box = SelectionBox(
                (cx * self.sub_chunk_size, 0, cz * self.sub_chunk_size),
                (
                    min((cx + 1) * self.sub_chunk_size, selection_box.size_x),
                    selection_box.size_y,
                    min((cz + 1) * self.sub_chunk_size, selection_box.size_z),
                ),
            )
            self._chunks[(cx, cz)] = (box, blocks[box.slice], data[box.slice], [], [])
        for e in block_entities:
            if all(key in e for key in ("x", "y", "z")):
                x, y, z = e["x"].value, e["y"].value, e["z"].value
                if (x, y, z) in selection_box:
                    cx = x >> 4
                    cz = z >> 4
                    self._chunks[(cx, cz)][3].append(e)
        for e in entities:
            if "Pos" in e:
                pos: PointCoordinates = tuple(
                    map(lambda t: float(t.value), e["Pos"].value)
                )
                if pos in selection_box:
                    cx = int(pos[0]) >> 4
                    cz = int(pos[2]) >> 4
                    self._chunks[(cx, cz)][4].append(e)

    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isfile(path) and path.endswith(".schematic")

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"java": (True, True), "bedrock": (True, True)}

    @property
    def extensions(self) -> Tuple[str, ...]:
        return (".schematic",)

    def _get_interface(self, raw_chunk_data=None) -> SchematicInterface:
        if self._platform == "java":
            return java_interface
        elif self._platform == "bedrock":
            return bedrock_interface
        else:
            raise Exception(f"{self._platform} is not a supported platform")

    def _get_interface_and_translator(
        self, raw_chunk_data=None
    ) -> Tuple["Interface", "Translator", VersionNumberAny]:
        interface = self._get_interface(raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            self.max_world_version, raw_chunk_data, self.translation_manager
        )
        return interface, translator, version_identifier

    def save_to(self, f: BinaryIO):
        if self._platform == "java":
            materials = "Alpha"
        elif self._platform == "bedrock":
            materials = "Pocket"
        else:
            raise ObjectWriteError(
                f'"{self._platform}" is not a supported platform for a schematic file.'
            )

        selection = self._bounds[self.dimensions[0]].selection_boxes[0]

        data = amulet_nbt.NBTFile(
            amulet_nbt.TAG_Compound(
                {
                    "TileTicks": amulet_nbt.TAG_List(),
                    "Width": amulet_nbt.TAG_Short(selection.size_x),
                    "Height": amulet_nbt.TAG_Short(selection.size_y),
                    "Length": amulet_nbt.TAG_Short(selection.size_z),
                    "Materials": amulet_nbt.TAG_String(materials),
                }
            ),
            "Schematic",
        )

        entities = []
        block_entities = []
        blocks = numpy.zeros(
            selection.shape, dtype=numpy.uint16
        )  # only 12 bits are actually used at most
        block_data = numpy.zeros(
            selection.shape, dtype=numpy.uint8
        )  # only 4 bits are used

        for (
            selection_,
            blocks_,
            data_,
            block_entities_,
            entities_,
        ) in self._chunks.values():
            if selection_.intersects(selection):
                box = selection_.create_moved_box(selection.min, subtract=True)
                blocks[box.slice] = blocks_
                block_data[box.slice] = data_
                for be in block_entities_:
                    coord_type = be["x"].__class__
                    be["x"] = coord_type(be["x"] - selection.min_x)
                    be["y"] = coord_type(be["y"] - selection.min_y)
                    be["z"] = coord_type(be["z"] - selection.min_z)
                    block_entities.append(be)
                for e in entities_:
                    coord_type = e["Pos"][0].__class__
                    e["Pos"][0] = coord_type(e["Pos"][0] - selection.min_x)
                    e["Pos"][1] = coord_type(e["Pos"][1] - selection.min_y)
                    e["Pos"][2] = coord_type(e["Pos"][2] - selection.min_z)
                    entities.append(e)

        data["Entities"] = amulet_nbt.TAG_List(entities)
        data["TileEntities"] = amulet_nbt.TAG_List(block_entities)
        data["Data"] = amulet_nbt.TAG_Byte_Array(
            numpy.transpose(block_data, (1, 2, 0))  # XYZ => YZX
        )
        data["Blocks"] = amulet_nbt.TAG_Byte_Array(
            numpy.transpose((blocks & 0xFF).astype(numpy.uint8), (1, 2, 0))
        )
        if numpy.max(blocks) > 0xFF:
            add_blocks = (numpy.transpose(blocks & 0xF00, (1, 2, 0)) >> 8).ravel()
            data["AddBlocks"] = amulet_nbt.TAG_Byte_Array(
                add_blocks[::2] + (add_blocks[1::2] << 4)
            )
        data.save_to(f)

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

    def _pack(
        self,
        chunk: "Chunk",
        translator: "Translator",
        chunk_version: VersionNumberAny,
    ) -> Tuple["Chunk", AnyNDArray]:
        version = self.translation_manager.get_version(
            *translator.translator_key(chunk_version)
        )
        palette = []
        for entry in chunk.block_palette.blocks:
            b = version.block.block_to_ints(entry)
            if b is None:
                b = (0, 0)
            palette.append(b)
        return (
            chunk,
            numpy.array(palette),
        )

    def _encode(
        self,
        interface: SchematicInterface,
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

    def _unpack(
        self,
        translator: "Translator",
        game_version: VersionNumberAny,
        chunk: "Chunk",
        chunk_palette: AnyNDArray,
    ) -> "Chunk":
        version = self.translation_manager.get_version(
            *translator.translator_key(game_version)
        )
        palette = chunk._block_palette = BlockManager()
        lut = numpy.array(
            [
                palette.get_add_block(version.block.ints_to_block(block, data))
                for block, data in chunk_palette
            ]
        )
        if len(palette.blocks) != len(chunk_palette):
            # if a blockstate was defined twice
            for cy in chunk.blocks.sub_chunks:
                chunk.blocks.add_sub_chunk(cy, lut[chunk.blocks.get_sub_chunk(cy)])

        return chunk

    def _delete_chunk(self, cx: int, cz: int, dimension: Optional[Dimension] = None):
        if (cx, cz) in self._chunks:
            del self._chunks[(cx, cz)]

    def _put_raw_chunk_data(
        self,
        cx: int,
        cz: int,
        section: SchematicChunk,
        dimension: Optional[Dimension] = None,
    ):
        self._chunks[(cx, cz)] = copy.deepcopy(
            (
                section.selection,
                section.blocks,
                section.data,
                section.block_entities,
                section.entities,
            )
        )

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: Optional[Dimension] = None
    ) -> SchematicChunk:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        if (cx, cz) in self._chunks:
            return SchematicChunk(*copy.deepcopy(self._chunks[(cx, cz)]))
        else:
            raise ChunkDoesNotExist

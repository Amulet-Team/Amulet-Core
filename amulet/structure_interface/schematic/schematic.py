from __future__ import annotations

import os
import numpy
from typing import List, Dict, Tuple, Generator

import amulet_nbt
from amulet.api.selection import SelectionBox
from amulet.api.data_types import PointCoordinates, ChunkCoordinates, PathOrBuffer
from amulet.api.errors import ChunkDoesNotExist

BlockArrayType = numpy.ndarray  # uint16 array
BlockDataArrayType = numpy.ndarray  # uint8 array


class SchematicChunk:
    def __init__(
        self,
        selection: SelectionBox,
        blocks: BlockArrayType,
        data: BlockDataArrayType,
        block_entities: List[amulet_nbt.TAG_Compound],
        entities: List[amulet_nbt.TAG_Compound],
    ):
        self.selection = selection
        assert isinstance(blocks, numpy.ndarray) and blocks.dtype == numpy.uint16
        assert isinstance(data, numpy.ndarray) and data.dtype == numpy.uint8
        self.blocks = blocks
        self.data = data
        self.block_entities = block_entities
        self.entities = entities


class SchematicReader:
    def __init__(self, path_or_buffer: PathOrBuffer):
        if isinstance(path_or_buffer, str):
            assert path_or_buffer.endswith(
                ".schematic"
            ), "File selected is not a .schematic file"
            assert os.path.isfile(
                path_or_buffer
            ), f"There is no schematic file at path {path_or_buffer}"
            schematic = amulet_nbt.load(path_or_buffer)
            assert not all(
                key in schematic for key in ("Version", "Data Version", "BlockData")
            ), "This file is not a legacy schematic file."
        else:
            assert hasattr(path_or_buffer, "read"), "Object does not have a read method"
            schematic = amulet_nbt.load(buffer=path_or_buffer)

        materials = schematic.get("Materials", amulet_nbt.TAG_String()).value
        if materials == "Alpha":
            self._platform = "java"
        elif materials == "Pocket":
            self._platform = "bedrock"
        else:
            raise Exception(
                f'"{materials}" is not a supported platform for a schematic file.'
            )
        self._chunks: Dict[
            ChunkCoordinates,
            Tuple[SelectionBox, BlockArrayType, BlockDataArrayType, list, list],
        ] = {}
        self._selection = SelectionBox(
            (0, 0, 0),
            (
                schematic["Width"].value,
                schematic["Height"].value,
                schematic["Length"].value,
            ),
        )
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
        max_point = self._selection.max
        temp_shape = (max_point[1], max_point[2], max_point[0])
        blocks = numpy.transpose(blocks.reshape(temp_shape), (2, 0, 1))  # YZX => XYZ
        data = numpy.transpose(
            schematic["Data"].value.reshape(temp_shape), (2, 0, 1)
        ).astype(numpy.uint8)
        for cx, cz in self._selection.chunk_locations():
            box = SelectionBox(
                (cx * 16, 0, cz * 16),
                (
                    min((cx + 1) * 16, self._selection.size_x),
                    self._selection.size_y,
                    min((cz + 1) * 16, self._selection.size_z),
                ),
            )
            self._chunks[(cx, cz)] = (box, blocks[box.slice], data[box.slice], [], [])
        for e in block_entities:
            if all(key in e for key in ("x", "y", "z")):
                x, y, z = e["x"].value, e["y"].value, e["z"].value
                if (x, y, z) in self._selection:
                    cx = x >> 4
                    cz = z >> 4
                    self._chunks[(cx, cz)][3].append(e)
        for e in entities:
            if "Pos" in e:
                pos: PointCoordinates = tuple(map(lambda t: t.value, e["Pos"].value))
                if pos in self._selection:
                    cx = int(pos[0]) >> 4
                    cz = int(pos[2]) >> 4
                    self._chunks[(cx, cz)][4].append(e)

    def read(self, cx: int, cz: int):
        if (cx, cz) in self._chunks:
            return SchematicChunk(*self._chunks[(cx, cz)])
        else:
            raise ChunkDoesNotExist

    @property
    def platform(self) -> str:
        return self._platform

    @property
    def selection(self) -> SelectionBox:
        return self._selection

    @property
    def chunk_coords(self) -> Generator[ChunkCoordinates, None, None]:
        yield from self._chunks.keys()

    def close(self):
        pass


class SchematicWriter:
    def __init__(self, path_or_buffer: str, platform: str, selection: SelectionBox):
        self._path_or_buffer = path_or_buffer
        if platform == "java":
            self._materials = "Alpha"
        elif platform == "bedrock":
            self._materials = "Pocket"
        else:
            raise Exception(
                f'"{platform}" is not a supported platform for a schematic file.'
            )
        self._selection = selection

        self._data = amulet_nbt.NBTFile(
            amulet_nbt.TAG_Compound(
                {
                    "TileTicks": amulet_nbt.TAG_List(),
                    "Width": amulet_nbt.TAG_Short(selection.size_x),
                    "Height": amulet_nbt.TAG_Short(selection.size_y),
                    "Length": amulet_nbt.TAG_Short(selection.size_z),
                    "Materials": amulet_nbt.TAG_String(self._materials),
                }
            ),
            "Schematic",
        )

        self._entities = []
        self._block_entities = []
        self._blocks = numpy.zeros(
            selection.shape, dtype=numpy.uint16
        )  # only 12 bits are actually used at most
        self._block_data = numpy.zeros(
            selection.shape, dtype=numpy.uint8
        )  # only 4 bits are used

    def write(self, section: SchematicChunk):
        if section.selection.intersects(self._selection):
            box = section.selection.create_moved_box(self._selection.min, subtract=True)
            self._blocks[box.slice] = section.blocks
            self._block_data[box.slice] = section.data
            for be in section.block_entities:
                coord_type = be["x"].__class__
                be["x"] = coord_type(be["x"] - self._selection.min_x)
                be["y"] = coord_type(be["y"] - self._selection.min_y)
                be["z"] = coord_type(be["z"] - self._selection.min_z)
                self._block_entities.append(be)
            for e in section.entities:
                coord_type = e["Pos"][0].__class__
                e["Pos"][0] = coord_type(e["Pos"][0] - self._selection.min_x)
                e["Pos"][1] = coord_type(e["Pos"][1] - self._selection.min_y)
                e["Pos"][2] = coord_type(e["Pos"][2] - self._selection.min_z)
                self._entities.append(e)

    def close(self):
        self._data["Entities"] = amulet_nbt.TAG_List(self._entities)
        self._data["TileEntities"] = amulet_nbt.TAG_List(self._block_entities)
        self._data["Data"] = amulet_nbt.TAG_Byte_Array(
            numpy.transpose(self._block_data, (1, 2, 0))  # XYZ => YZX
        )
        self._data["Blocks"] = amulet_nbt.TAG_Byte_Array(
            numpy.transpose((self._blocks & 0xFF).astype(numpy.uint8), (1, 2, 0))
        )
        if numpy.max(self._blocks) > 0xFF:
            add_blocks = numpy.transpose(self._blocks & 0xF00, (1, 2, 0)) >> 8
            self._data["AddBlocks"] = amulet_nbt.TAG_Byte_Array(
                add_blocks[::2] + (add_blocks[1::2] << 4)
            )
        self._data.save_to(self._path_or_buffer)

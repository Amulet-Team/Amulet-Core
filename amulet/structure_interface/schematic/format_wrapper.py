import os
from typing import Optional, Tuple, Generator, TYPE_CHECKING, BinaryIO, Dict
import numpy

import amulet_nbt

from amulet import log
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
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ObjectReadError, ObjectWriteError
from .schematic import SchematicWriter, SchematicReader, SchematicChunk
from .interface import (
    JavaSchematicInterface,
    BedrockSchematicInterface,
    SchematicInterface,
)

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface

java_interface = JavaSchematicInterface()
bedrock_interface = BedrockSchematicInterface()

BlockArrayType = numpy.ndarray  # uint16 array
BlockDataArrayType = numpy.ndarray  # uint8 array


class SchematicFormatWrapper(StructureFormatWrapper):
    def __init__(self, path: str):
        super().__init__(path)
        self._chunks: Dict[
            ChunkCoordinates,
            Tuple[SelectionBox, BlockArrayType, BlockDataArrayType, list, list],
        ] = {}

    def _create(self):
        self._chunks = {}

    def open_from(self, f: BinaryIO):
        schematic = amulet_nbt.load(f)
        if any(key in schematic for key in ("Version", "Data Version", "BlockData")):
            raise ObjectReadError("This file is not a legacy schematic file.")
        materials = schematic.get("Materials", amulet_nbt.TAG_String()).value
        if materials == "Alpha":
            self._platform = "java"
        elif materials == "Pocket":
            self._platform = "bedrock"
        else:
            raise Exception(
                f'"{materials}" is not a supported platform for a schematic file.'
            )
        self._chunks = {}
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
        blocks: numpy.ndarray = schematic["Blocks"].value.astype(numpy.uint8).astype(
            numpy.uint16
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
                (cx * self.sub_chunk_size, 0, cz * self.sub_chunk_size),
                (
                    min((cx + 1) * self.sub_chunk_size, self._selection.size_x),
                    self._selection.size_y,
                    min((cz + 1) * self.sub_chunk_size, self._selection.size_z),
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
                pos: PointCoordinates = tuple(map(lambda t: float(t.value), e["Pos"].value))
                if pos in self._selection:
                    cx = int(pos[0]) >> 4
                    cz = int(pos[2]) >> 4
                    self._chunks[(cx, cz)][4].append(e)

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        Returns whether this format is able to load the given object.

        :param path: The path of the object to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        return os.path.isfile(path) and path.endswith(".schematic")

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"java": (True, True), "bedrock": (True, True)}

    @property
    def extensions(self) -> Tuple[str, ...]:
        return ".schematic",

    def _get_interface(
        self, max_world_version, raw_chunk_data=None
    ) -> SchematicInterface:
        if self._platform == "java":
            return java_interface
        elif self._platform == "bedrock":
            return bedrock_interface
        else:
            raise Exception(f"{self._platform} is not a supported platform")

    def _get_interface_and_translator(
        self, max_world_version, raw_chunk_data=None
    ) -> Tuple["Interface", "Translator", VersionNumberAny]:
        interface = self._get_interface(max_world_version, raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            max_world_version, raw_chunk_data, self.translation_manager
        )
        return interface, translator, version_identifier

    def _save(self):
        """Save the data back to the disk database"""
        raise NotImplementedError

    def save_to(self, f: BinaryIO):
        raise NotImplementedError

    def _close(self):
        """Close the disk database"""
        self._data.close()

    def unload(self):
        """Unload data stored in the Format class"""
        raise NotImplementedError

    def all_chunk_coords(
        self, dimension: Optional[Dimension] = None
    ) -> Generator[Tuple[int, int], None, None]:
        """A generator of all chunk coords"""
        if self._mode == "r":
            yield from self._data.chunk_coords
        else:
            raise ObjectReadError("all_chunk_coords is only valid in read mode")

    def _pack(
        self, chunk: "Chunk", translator: "Translator", chunk_version: VersionNumberAny,
    ) -> Tuple["Chunk", AnyNDArray]:
        version = self.translation_manager.get_version(
            *translator.translator_key(chunk_version)
        )
        return (
            chunk,
            numpy.array(
                [
                    version.block.block_to_ints(block)
                    for block in chunk.block_palette.blocks()
                ]
            ),
        )

    def _encode(
        self, chunk: Chunk, chunk_palette: AnyNDArray, interface: SchematicInterface,
    ):
        return interface.encode(
            chunk,
            chunk_palette,
            self.max_world_version,
            SelectionBox.create_chunk_box(chunk.cx, chunk.cz).intersection(
                self._selection
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
        if len(palette.blocks()) != len(chunk_palette):
            # if a blockstate was defined twice
            for cy in chunk.blocks.sub_chunks:
                chunk.blocks.add_sub_chunk(cy, lut[chunk.blocks.get_sub_chunk(cy)])

        return chunk

    def _delete_chunk(self, cx: int, cz: int, dimension: Optional[Dimension] = None):
        raise ObjectWriteError(
            "delete_chunk is not a valid method for a schematic file"
        )

    def _put_raw_chunk_data(
        self,
        cx: int,
        cz: int,
        data: SchematicChunk,
        dimension: Optional[Dimension] = None,
    ):
        """
        Actually stores the data from the interface to disk.
        """
        if self._mode == "w":
            self._data.write(data)
        else:
            raise ObjectWriteError("The schematic file is not open for writing.")

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
        if self._mode == "r":
            return self._data.read(cx, cz)
        else:
            raise ObjectReadError("The schematic file is not open for reading.")

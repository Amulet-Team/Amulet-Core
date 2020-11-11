import os
from typing import Optional, Union, Tuple, Generator, TYPE_CHECKING
import numpy

from amulet import log
from amulet.api.data_types import (
    AnyNDArray,
    VersionNumberAny,
    PathOrBuffer,
)
from amulet.api.registry import BlockManager
from amulet.api.wrapper import StructureFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ObjectReadError, ObjectWriteError
from .schematic import SchematicWriter, SchematicReader, SchematicChunk
from .interface import (
    JavaSchematicInterface,
    BedrockSchematicInerface,
    SchematicInterface,
)

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface

java_interface = JavaSchematicInterface()
bedrock_interface = BedrockSchematicInerface()


class SchematicFormatWrapper(StructureFormatWrapper):
    def __init__(self, path: PathOrBuffer, mode: str = "r"):
        super().__init__(path)
        assert mode in ("r", "w"), 'Mode must be either "r" or "w".'
        self._mode = mode
        if isinstance(path, str):
            assert path.endswith(".schematic"), 'Path must end with ".schematic"'
            if mode == "r":
                assert os.path.isfile(path), "File specified does not exist."
        self._data: Optional[Union[SchematicWriter, SchematicReader]] = None
        self._open = False
        self._platform = "java"
        self._version = (1, 12, 2)
        self._selection: SelectionBox = SelectionBox((0, 0, 0), (0, 0, 0))

    def open(self):
        """Open the database for reading and writing"""
        if self._open:
            return
        if self._mode == "r":
            assert (
                isinstance(self.path_or_buffer, str)
                and os.path.isfile(self.path_or_buffer)
            ) or hasattr(self.path_or_buffer, "read"), "File specified does not exist."
            self._data = SchematicReader(self.path_or_buffer)
            self._platform = self._data.platform
            self._selection = self._data.selection
        else:
            self._data = SchematicWriter(
                self.path_or_buffer,
                self.platform,
                self._selection,
            )
        self._open = True

    @property
    def readable(self) -> bool:
        """Can this object have data read from it."""
        return self._mode == "r"

    @property
    def writeable(self) -> bool:
        """Can this object have data written to it."""
        return self._mode == "w"

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        Returns whether this format is able to load the given object.

        :param path: The path of the object to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        return os.path.isfile(path) and path.endswith(".schematic")

    @property
    def platform(self) -> str:
        """Platform string ("bedrock" / "java" / ...)"""
        return self._platform

    @platform.setter
    def platform(self, platform: str):
        if self._open:
            log.error(
                "Construction platform cannot be changed after the object has been opened."
            )
            return
        self._platform = platform

    @property
    def version(self) -> Tuple[int, int, int]:
        return self._version

    @version.setter
    def version(self, version: Tuple[int, int, int]):
        if self._open:
            log.error(
                "Construction version cannot be changed after the object has been opened."
            )
            return
        self._version = version

    @property
    def selection(self) -> SelectionGroup:
        """The box that is selected"""
        return SelectionGroup([self._selection])

    @selection.setter
    def selection(self, selection: SelectionGroup):
        if self._open:
            log.error(
                "Construction selection cannot be changed after the object has been opened."
            )
            return
        if selection.selection_boxes:
            self._selection = selection.selection_boxes[0]
        else:
            raise Exception("Given selection box is empty")

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

    @property
    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        return True

    def save(self):
        """Save the data back to the disk database"""
        pass

    def close(self):
        """Close the disk database"""
        self._data.close()

    def unload(self):
        """Unload data stored in the Format class"""
        pass

    def all_chunk_coords(self, *args) -> Generator[Tuple[int, int], None, None]:
        """A generator of all chunk coords"""
        if self._mode == "r":
            yield from self._data.chunk_coords
        else:
            raise ObjectReadError("all_chunk_coords is only valid in read mode")

    def _pack(
        self,
        chunk: "Chunk",
        translator: "Translator",
        chunk_version: VersionNumberAny,
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
        self,
        chunk: Chunk,
        chunk_palette: AnyNDArray,
        interface: SchematicInterface,
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

    def delete_chunk(self, cx: int, cz: int, *args):
        raise ObjectWriteError(
            "delete_chunk is not a valid method for a schematic file"
        )

    def _put_raw_chunk_data(self, cx: int, cz: int, data: SchematicChunk, *args):
        """
        Actually stores the data from the interface to disk.
        """
        if self._mode == "w":
            self._data.write(data)
        else:
            raise ObjectWriteError("The schematic file is not open for writing.")

    def _get_raw_chunk_data(self, cx: int, cz: int, *args) -> SchematicChunk:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The raw chunk data.
        """
        if self._mode == "r":
            return self._data.read(cx, cz)
        else:
            raise ObjectReadError("The schematic file is not open for reading.")

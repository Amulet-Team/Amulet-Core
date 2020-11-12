import os
from typing import Optional, Union, Tuple, Generator, TYPE_CHECKING

from amulet import log
from amulet.api.data_types import (
    VersionNumberAny,
    PathOrBuffer,
    ChunkCoordinates,
    AnyNDArray,
)
from amulet.api.wrapper import StructureFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ObjectReadError, ObjectWriteError

from .mcstructure import MCStructureWriter, MCStructureReader, MCStructureChunk
from .interface import MCStructureInterface

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface

mcstructure_interface = MCStructureInterface()


class MCStructureFormatWrapper(StructureFormatWrapper):
    def __init__(self, path: PathOrBuffer, mode: str = "r"):
        super().__init__(path)
        assert mode in ("r", "w"), 'Mode must be either "r" or "w".'
        self._mode = mode
        if isinstance(path, str):
            assert path.endswith(".mcstructure"), 'Path must end with ".mcstructure"'
            if mode == "r":
                assert os.path.isfile(path), "File specified does not exist."
        self._data: Optional[Union[MCStructureWriter, MCStructureReader]] = None
        self._open = False
        self._platform = "bedrock"
        self._version = (1, 15, 2)
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
            self._data = MCStructureReader(self.path_or_buffer)
            self._selection = self._data.selection
        else:
            self._data = MCStructureWriter(
                self.path_or_buffer,
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
    def is_valid(path: PathOrBuffer) -> bool:
        """
        Returns whether this format is able to load the given object.

        :param path: The path of the object to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        return os.path.isfile(path) and path.endswith(".mcstructure")

    @property
    def platform(self) -> str:
        """Platform string ("bedrock" / "java" / ...)"""
        return self._platform

    @property
    def version(self) -> Tuple[int, int, int]:
        return self._version

    @version.setter
    def version(self, version: Tuple[int, int, int]):
        if self._open:
            log.error(
                "mcstructure version cannot be changed after the object has been opened."
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
                "mcstructure selection cannot be changed after the object has been opened."
            )
            return
        if selection.selection_boxes:
            self._selection = selection.selection_boxes[0]
        else:
            raise Exception("Given selection box is empty")

    def _get_interface(
        self, max_world_version, raw_chunk_data=None
    ) -> "MCStructureInterface":
        return mcstructure_interface

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

    def all_chunk_coords(self, *args) -> Generator[ChunkCoordinates, None, None]:
        """A generator of all chunk coords"""
        if self._mode == "r":
            yield from self._data.chunk_coords
        else:
            raise ObjectReadError("all_chunk_coords is only valid in read mode")

    def _encode(
        self,
        chunk: Chunk,
        chunk_palette: AnyNDArray,
        interface: MCStructureInterface,
    ):
        return interface.encode(
            chunk,
            chunk_palette,
            self.max_world_version,
            SelectionBox.create_chunk_box(chunk.cx, chunk.cz).intersection(
                self._selection
            ),
        )

    def delete_chunk(self, cx: int, cz: int, *args):
        raise ObjectWriteError(
            "delete_chunk is not a valid method for an mcstructure file"
        )

    def _put_raw_chunk_data(self, cx: int, cz: int, section: MCStructureChunk, *args):
        """
        Actually stores the data from the interface to disk.
        """
        if self._mode == "w":
            self._data.write(section)
        else:
            raise ObjectWriteError("The mcstructure file is not open for writing.")

    def _get_raw_chunk_data(self, cx: int, cz: int, *args) -> MCStructureChunk:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The raw chunk data.
        """
        if self._mode == "r":
            return self._data.read(cx, cz)
        else:
            raise ObjectReadError("The mcstructure file is not open for reading.")

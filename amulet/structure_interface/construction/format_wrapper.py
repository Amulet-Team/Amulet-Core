import os
from typing import Optional, Union, List, Tuple, Dict, Generator
import numpy

from amulet import log
from amulet.api.wrapper import FormatWraper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ObjectReadError, ObjectWriteError, ChunkDoesNotExist

from .construction import ConstructionWriter, ConstructionReader, ConstructionSection
from .interface import Construction0Interface, ConstructionInterface

construction_0_interface = Construction0Interface()


class ConstructionFormatWrapper(FormatWraper):
    def __init__(self, path, mode='r'):
        super().__init__(path)
        assert mode in ('r', 'w'), 'Mode must be either "r" or "w".'
        self._mode = mode
        assert path.endswith('.construction'), 'Path must end with ".construction"'
        if mode == 'r':
            assert os.path.isfile(path), 'File specified does not exist.'
        self._data: Optional[Union[ConstructionWriter, ConstructionReader]] = None
        self._open = False
        self._platform = 'java'
        self._version = (1, 15, 2)
        self._selection: SelectionGroup = SelectionGroup()

        # used to look up which sections are in a given chunk when loading
        self._chunk_to_section: Optional[Dict[Tuple[int, int], List[int]]] = None

        # used to look up which selection boxes intersect a given chunk (boxes are clipped to the size of the chunk)
        self._chunk_to_box: Optional[Dict[Tuple[int, int], List[SelectionBox]]] = None

    @property
    def readable(self) -> bool:
        """Can this object have data read from it."""
        return self._mode == 'r'

    @property
    def writeable(self) -> bool:
        """Can this object have data written to it."""
        return self._mode == 'w'

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        Returns whether this format is able to load the given object.

        :param path: The path of the object to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        return os.path.isfile(path) and path.endswith('.construction')

    @property
    def platform(self) -> str:
        """Platform string ("bedrock" / "java" / ...)"""
        return self._platform

    @platform.setter
    def platform(self, platform: str):
        if self._open:
            log.error('Construction platform cannot be changed after the object has been opened.')
            return
        self._platform = platform

    @property
    def version(self) -> Tuple[int, int, int]:
        return self._version

    @version.setter
    def version(self, version: Tuple[int, int, int]):
        if self._open:
            log.error('Construction version cannot be changed after the object has been opened.')
            return
        self._version = version

    @property
    def selection(self) -> SelectionGroup:
        """Platform string ("bedrock" / "java" / ...)"""
        return self._selection

    @selection.setter
    def selection(self, selection: SelectionGroup):
        if self._open:
            log.error('Construction selection cannot be changed after the object has been opened.')
            return
        self._selection = selection

    def _get_interface(
        self, max_world_version, raw_chunk_data=None
    ) -> 'ConstructionInterface':
        return construction_0_interface

    def open(self):
        """Open the database for reading and writing"""
        if self._mode == 'r':
            assert os.path.isfile(self.path), 'File specified does not exist.'
            self._data = ConstructionReader(self.path)
            self._chunk_to_section.clear()
            for index, (x, _, z, _, _, _, _, _) in enumerate(self._data.sections):
                cx = x >> 4
                cz = z >> 4
                self._chunk_to_section.setdefault((cx, cz), []).append(index)
        else:
            self._data = ConstructionWriter(
                self.path,
                self.platform,
                self.version,
                [box.bounds for box in self.selection.selection_boxes]
            )
            self._chunk_to_box = {}
            for box in self.selection.selection_boxes:
                for cx, cz in box.chunk_locations():
                    self._chunk_to_box.setdefault((cx, cz), []).append(box.intersection(SelectionBox.create_chunk_box(cx, cz)))
        self._open = True

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

    def all_chunk_coords(self, *args) -> Generator[Tuple[int, int]]:
        """A generator of all chunk coords"""
        if self._mode == 'r':
            yield from self._chunk_to_section.keys()
        else:
            raise ObjectReadError('all_chunk_coords is only valid in read mode')

    def _encode(self, chunk: Chunk, chunk_palette: numpy.ndarray, interface: ConstructionInterface):
        return interface.encode(
            chunk, chunk_palette, self.max_world_version, self._chunk_to_box.get((chunk.cx, chunk.cz))
        )

    def delete_chunk(self, cx: int, cz: int, *args):
        raise ObjectWriteError('delete_chunk is not a valid method for a construction file')

    def _put_raw_chunk_data(self, cx: int, cz: int, data: List[ConstructionSection], *args):
        """
        Actually stores the data from the interface to disk.
        """
        if self._mode == 'w':
            for section in data:
                self._data.write(section)
        else:
            raise ObjectWriteError('The construction file is not open for writing.')

    def _get_raw_chunk_data(self, cx: int, cz: int, *args) -> List[ConstructionSection]:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The raw chunk data.
        """
        if self._mode == 'r':
            if (cx, cz) in self._chunk_to_section:
                return [self._data.read(index) for index in self._chunk_to_section[(cx, cz)]]
            else:
                raise ChunkDoesNotExist
        else:
            raise ObjectReadError('The construction file is not open for reading.')

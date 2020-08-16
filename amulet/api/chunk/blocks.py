import numpy
from typing import Iterable

from amulet.api.partial_array.partial_array import PartialNDArray


class Blocks(PartialNDArray):
    _size_x = 16
    _section_size_y = 16
    _size_z = 16

    def _check_type(self, other) -> bool:
        return isinstance(other, Blocks)

    @property
    def sub_chunks(self) -> Iterable[int]:
        """An iterable of the sub-chunk indexes that exist"""
        return self.sections

    def get_create_sub_chunk(self, cy: int) -> numpy.ndarray:
        """Get the section ndarray for a given section index. Create if it does not exist.
        :param cy: The section y index
        :return: Numpy array for this section
        """
        return self.get_create_section(cy)

    def get_sub_chunk(self, cy: int) -> numpy.ndarray:
        """Get the section ndarray for a given section index.
        :param cy: The section y index
        :return: Numpy array for this section
        :raises: KeyError if no section exists with this index
        """
        return self.get_section(cy)

    def add_sub_chunk(self, cy: int, sub_chunk: numpy.ndarray):
        """Add a sub-chunk. Overwrite if already exists
        :param cy: The section y index
        :param sub_chunk: The Numpy array to add at this location
        :return:
        """
        self.add_section(cy, sub_chunk)

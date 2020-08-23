import numpy
from typing import Iterable

from amulet.api.partial_3d_array import Partial3DArray


class Blocks(Partial3DArray):
    def __init__(self):
        super().__init__(
            numpy.uint32,
            0,
            (16, 16, 16),
            (None, None, None),
            (None, None, None),
            (None, None, None),
        )

    @property
    def sub_chunks(self) -> Iterable[int]:
        """An iterable of the sub-chunk indexes that exist"""
        return self.sections

    def get_sub_chunk(self, cy: int) -> numpy.ndarray:
        """Get the section ndarray for a given section index.
        :param cy: The section y index
        :return: Numpy array for this section
        """
        return self.get_section(cy)

    def add_sub_chunk(self, cy: int, sub_chunk: numpy.ndarray):
        """Add a sub-chunk. Overwrite if already exists
        :param cy: The section y index
        :param sub_chunk: The Numpy array to add at this location
        :return:
        """
        self.add_section(cy, sub_chunk)

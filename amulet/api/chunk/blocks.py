import numpy
from typing import Iterable, Optional, Union, Dict
from copy import deepcopy

from amulet.api.partial_3d_array import UnboundedPartial3DArray


class Blocks(UnboundedPartial3DArray):
    def __init__(
        self,
        input_array: Optional[Union[Dict[int, numpy.ndarray], "Blocks"]] = None,
    ):
        if input_array is None:
            input_array = {}
        if isinstance(input_array, Blocks):
            input_array: dict = deepcopy(input_array._sections)
        if not isinstance(input_array, dict):
            raise Exception(f"Input array must be Blocks or dict, got {input_array}")
        super().__init__(numpy.uint32, 0, (16, 16, 16), (0, 16), sections=input_array)

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

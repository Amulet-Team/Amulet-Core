import typing
from typing import Union, Sequence

import numpy

def method_not_implemented(*args, **kwargs):
    raise NotImplementedError()

class _InternalMappingHandler:

    def __init__(self):
        #self._mapping = {"minecraft:air": 0}
        #self._reverse_mapping = {0: "minecraft:air"}
        self._mapping = ["minecraft:air"]
        self._next_id = 1
        self.__getitem__ = self._mapping.__getitem__
        self.__contains__ = self._mapping.__contains__

    def add_entry(self, entry: str) -> int:
        if entry in self._mapping:
            return self.get_entry(entry)
        self._mapping[self._next_id] = entry
        self._next_id += 1
        return self._next_id - 1

    def get_entry(self, entry: str) -> int:
        return self._mapping.index(entry)

class UnifiedWorld:

    def __init__(self, directory, root_tag, wrapper):
        self._directory = directory
        self._root_tag = root_tag
        self._wrapper = wrapper
        self.mapping_handler = _InternalMappingHandler()

        self._load_space()

        self._blocks = numpy.zeros((256, 256, 256), dtype=numpy.uint16)

    def _load_space(self):
        #print(self._root_tag)
        self._wrapper.d_load_chunk(0,0)

    def get_block(self, x: int, y: int, z: int) -> str:
        if not (0 <= y <= 255):
            raise IndexError("The supplied Y coordinate must be between 0 and 255")

        return self._blocks[x, y, z]

    def get_blocks(self, *args: Union[Sequence[slice], Sequence[int]]) -> numpy.ndarray:
        length = len(args)
        if 3 <= length < 6:
            s_x, s_y, s_z = args[0:3]
            if not (
                isinstance(s_x, slice)
                and isinstance(s_y, slice)
                and isinstance(s_z, slice)
            ):
                raise IndexError()

            return self.get_blocks_slice(s_x, s_y, s_z)

    def get_blocks_slice(
        self, x_slice: slice, y_slice: slice, z_slice: slice
    ) -> numpy.ndarray:
        return self._blocks[x_slice, y_slice, z_slice]

    def get_blocks_bounded(self, *args: Sequence[int]) -> numpy.ndarray:
        return self._blocks[args[0]:args[1], args[2]:args[3], args[4]:args[5]]

    def get_blocks_stepped(self, *args: Sequence[int]) -> numpy.ndarray:
        return self._blocks[
            args[0]:args[1]:args[6], args[2]:args[3]:args[7], args[4]:args[5]:args[8]
        ]

from typing import Tuple, Union, Optional, Callable

import numpy

PointCoordinates = Tuple[int, int, int]
SliceCoordinates = Tuple[slice, slice, slice]


class Chunk:
    def __init__(self, cx: int, cz: int, get_chunk_func: Callable[[int, int], Tuple[numpy.ndarray, dict, dict]]):
        self.cx = cx
        self.cz = cz
        self.get_chunk_func = get_chunk_func
        self.changed = False
        self._blocks: Optional[numpy.ndarray] = None

    @property
    def blocks(self):
        if self._blocks is not None:
            return self._blocks
        self._blocks = self.get_chunk_func(self.cx, self.cz)[0]
        self._blocks.setflags(write=False)
        return self._blocks

    @blocks.setter
    def blocks(self, value: numpy.ndarray):
        if not (self._blocks == value).all():
            self.changed = True
        self._blocks = value

    def __getitem__(self, item: Union[PointCoordinates, SliceCoordinates]):
        if not isinstance(item, tuple) or len(item) != 3 or not (
                isinstance(item[0], int) and isinstance(item[1], int) and isinstance(item[2], int) or (isinstance(item[0], slice) and isinstance(item[1], slice) and isinstance(item[2], slice))):
            raise Exception(f"The item {item} for Selection object does not make sense")
        return SubChunk(item, self)


class SubChunk:
    def __init__(self, sub_selection_slice: Union[PointCoordinates, SliceCoordinates], parent: Chunk):
        self._sub_selection_slice = sub_selection_slice
        self._parent = parent

    @property
    def blocks(self):
        return self._parent.blocks[self._sub_selection_slice]

    @blocks.setter
    def blocks(self, value):
        temp_blocks = self._parent.blocks.copy()
        temp_blocks[self._sub_selection_slice] = value
        self._parent.blocks = temp_blocks

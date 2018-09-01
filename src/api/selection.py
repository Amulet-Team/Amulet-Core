from typing import Tuple, Union

import numpy

PointCoordinates = Tuple[int, int, int]
SliceCoordinates = Tuple[slice, slice, slice]


class AbstractSelection:
    blocks: numpy.ndarray = None


class Selection(AbstractSelection):
    def __init__(self, blocks: numpy.ndarray):
        self._blocks = blocks
        self._blocks.setflags(write=False)

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, value):
        self._blocks = value

    def __getitem__(self, item: Union[PointCoordinates, SliceCoordinates]):
        if not isinstance(item, tuple) or len(item) != 3 or not (
                isinstance(item[0], int) and isinstance(item[1], int) and isinstance(item[2], int) or (isinstance(item[0], slice) and isinstance(item[1], slice) and isinstance(item[2], slice))):
            raise Exception(f"The item {item} for Selection object does not make sense")
        return SubSelection(item, self)


class SubSelection(AbstractSelection):
    def __init__(self, sub_selection_slice: Union[PointCoordinates, SliceCoordinates],
                 parent: Union[Selection, "SubSelection"]):
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

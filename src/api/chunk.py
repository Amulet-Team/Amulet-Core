from __future__ import annotations

import os
from gzip import GzipFile
from copy import deepcopy
from typing import Tuple, Union, Optional, Callable

import numpy

PointCoordinates = Tuple[int, int, int]
SliceCoordinates = Tuple[slice, slice, slice]


class Chunk:
    def __init__(
        self, cx: int, cz: int, get_blocks_func: Callable[[int, int], numpy.ndarray]
    ):
        self.cx = cx
        self.cz = cz
        self.get_blocks_func = get_blocks_func
        self.previous_unsaved_state: Optional[Chunk] = None
        self.changed: bool = False
        self._blocks: Optional[numpy.ndarray] = None
        self._entities = []

    @property
    def blocks(self):
        if self._blocks is None:
            self._blocks = self.get_blocks_func(self.cx, self.cz)
        self._blocks.setflags(write=False)
        return self._blocks

    @blocks.setter
    def blocks(self, value: numpy.ndarray):
        if not (self._blocks == value).all():
            if self.previous_unsaved_state is None:
                self.previous_unsaved_state = deepcopy(self)
            self.changed = True
        self._blocks = value

    @property
    def entities(self):
        return deepcopy(self._entities)

    @entities.setter
    def entities(self, value):
        if not self._entities and value:
            if self.previous_unsaved_state is None:
                self.previous_unsaved_state = deepcopy(self)
            self.changed = True
        self._entities = value

    def __getitem__(self, item: Union[PointCoordinates, SliceCoordinates]):
        if (
            not isinstance(item, tuple)
            or len(item) != 3
            or not (
                isinstance(item[0], int)
                and isinstance(item[1], int)
                and isinstance(item[2], int)
                or (
                    isinstance(item[0], slice)
                    and isinstance(item[1], slice)
                    and isinstance(item[2], slice)
                )
            )
        ):
            raise Exception(f"The item {item} for Selection object does not make sense")

        return SubChunk(item, self)

    def __deepcopy__(self, memo):
        chunk = Chunk(self.cx, self.cz, self.get_blocks_func)
        if self._blocks:
            chunk._blocks = self._blocks.copy()
        if self._entities:
            chunk._entities = deepcopy(self._entities)
        return chunk

    def save_to_file(self, path: str, compressed=False):
        path = os.path.join(path, f"chunk_{self.cx}_{self.cz}")
        os.makedirs(path, exist_ok=True)
        blocks_file = os.path.join(path, "blocks.npy")
        if compressed:
            blocks_file = GzipFile(f"{blocks_file}.gz", "w")
        numpy.save(blocks_file, self._blocks, allow_pickle=False, fix_imports=False)

    def load_from_file(self, path: str):
        path = os.path.join(path, f"chunk_{self.cx}_{self.cz}")
        blocks_file = os.path.join(path, "blocks.npy")
        if not os.path.exists(blocks_file):
            if not os.path.exists(f"{blocks_file}.gz"):
                raise Exception(f"The needed blocks file in path {path} does not exist")

            blocks_file = GzipFile(f"{blocks_file}.gz", "r")
        self._blocks = numpy.load(blocks_file, allow_pickle=False, fix_imports=False)


class SubChunk:
    def __init__(
        self,
        sub_selection_slice: Union[PointCoordinates, SliceCoordinates],
        parent: Chunk,
    ):
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

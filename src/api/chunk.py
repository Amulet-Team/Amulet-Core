from __future__ import annotations

import copy
from os.path import join
import pickle
from typing import Tuple, Union

import numpy

PointCoordinates = Tuple[int, int, int]
SliceCoordinates = Tuple[slice, slice, slice]


class Chunk:
    def __init__(self, cx: int, cz: int, blocks=None, entities=None, tileentities=None):
        self.cx, self.cz = cx, cz
        self._blocks: numpy.ndarray = blocks
        self._entities = entities
        self._tileentities = tileentities

        self._changed = False
        self._marked_for_deletion = False

    def __repr__(self):
        return f"Chunk({self.cx}, {self.cx}, {repr(self._blocks)}, {repr(self._entities)}, {repr(self._tileentities)})"

    def __getitem__(self, item):
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

    @property
    def changed(self) -> bool:
        return self._changed

    @property
    def marked_for_deletion(self) -> bool:
        return self._marked_for_deletion

    @property
    def blocks(self) -> numpy.ndarray:
        self._blocks.setflags(write=False)
        return self._blocks

    @blocks.setter
    def blocks(self, value: numpy.ndarray):
        if not (self._blocks == value).all():
            self._changed = True
        self._blocks = value

    @property
    def entities(self):
        return copy.deepcopy(self._entities)

    @entities.setter
    def entities(self, value):
        if self._entities != value:
            self._changed = True
            self._entities = value

    @property
    def tileentities(self):
        return copy.deepcopy(self._tileentities)

    @tileentities.setter
    def tileentities(self, value):
        if self._tileentities != value:
            self._changed = True
            self._tileentities = value

    def delete(self):
        self._marked_for_deletion = True
        self._changed = True

    def save_blocks_to_file(self, change_path) -> str:
        save_path = join(change_path, "blocks.npy")
        numpy.save(save_path, self._blocks, allow_pickle=False, fix_imports=False)

        return save_path

    def save_entities_to_file(self, change_path) -> str:
        save_path = join(change_path, "entities.pickle")
        fp = open(save_path, "wb")
        pickle.dump(self._entities, fp)
        fp.close()

        return save_path

    def save_tileentities_to_file(self, change_path) -> str:
        save_path = join(change_path, "tileentities.pickle")
        fp = open(save_path, "wb")
        pickle.dump(self._tileentities, fp)
        fp.close()

        return save_path


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

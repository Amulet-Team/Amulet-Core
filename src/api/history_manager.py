from __future__ import annotations

import copy
from typing import Dict, List, Tuple

import os

import pickle

import numpy


class SubChunk2:
    def __init__(self, sub_selection_slice, parent: Chunk2):
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


class Chunk2:
    def __init__(self, cx: int, cz: int, blocks=None, entities=None, tileentities=None):
        self.cx, self.cz = cx, cz
        self._blocks: numpy.ndarray = blocks
        self._entities = entities
        self._tileentities = tileentities

        self._changed = False

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

        return SubChunk2(item, self)

    @property
    def changed(self) -> bool:
        return self._changed

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

    def save_blocks_to_file(self, change_no: int, base_path=".") -> str:
        change_path = os.path.join(base_path, str(change_no), f"{self.cx},{self.cz}")

        if not os.path.exists(change_path):
            os.makedirs(change_path, exist_ok=True)

        save_path = os.path.join(change_path, "blocks.npy")
        numpy.save(save_path, self._blocks, allow_pickle=False, fix_imports=False)

        return save_path

    def save_entities_to_file(self, change_no: int, base_path=".") -> str:
        change_path = os.path.join(base_path, str(change_no), f"{self.cx},{self.cz}")

        if not os.path.exists(change_path):
            os.makedirs(change_path, exist_ok=True)

        save_path = os.path.join(change_path, "entities.pickle")
        fp = open(save_path, "wb")
        pickle.dump(self._entities, fp)
        fp.close()

        return save_path

    def save_tileentities_to_file(self, change_no: int, base_path=".") -> str:
        change_path = os.path.join(base_path, str(change_no), f"{self.cx},{self.cz}")

        if not os.path.exists(change_path):
            os.makedirs(change_path, exist_ok=True)

        save_path = os.path.join(change_path, "tileentities.pickle")
        fp = open(save_path, "wb")
        pickle.dump(self._tileentities, fp)
        fp.close()

        return save_path


class ChunkHistoryManager:
    def __init__(self, work_dir: str = "."):
        self._history: List[Dict[Tuple[int, int], Dict[str, str]]] = [{}]
        self._change_index: int = 0
        self.work_dir: str = work_dir

    @property
    def change_index(self) -> int:
        return self._change_index

    def add_original_chunk(self, chunk: Chunk2):

        self._history[0][(chunk.cx, chunk.cz)] = self.serialize_chunk(chunk, 0)

    def add_changed_chunks(self, chunks: List[Chunk2]):
        self._change_index += 1
        change_no = self._change_index
        change_manifest = {}

        if change_no < len(self._history):
            raise NotImplementedError()

        if change_no == 0:
            raise NotImplementedError()

        for chunk in chunks:
            change_manifest[(chunk.cx, chunk.cz)] = self.serialize_chunk(
                chunk, change_no
            )

        self._history.append(change_manifest)

    def serialize_chunk(self, chunk: Chunk2, change_no: int) -> Dict[str, str]:
        serialized_chunk = {
            "blocks": chunk.save_blocks_to_file(change_no, base_path=self.work_dir),
            "entities": chunk.save_entities_to_file(change_no, base_path=self.work_dir),
            "tileentities": chunk.save_tileentities_to_file(
                change_no, base_path=self.work_dir
            ),
            "action": "EDIT",
        }
        chunk._changed = False
        return serialized_chunk

    def _unserialize_chunks(self) -> List[Chunk2]:
        chunks = []

        for chunk_coords, chunk_manifest in self._history[self._change_index].items():
            blocks = numpy.load(
                chunk_manifest["blocks"], allow_pickle=False, fix_imports=False
            )

            fp = open(chunk_manifest["entities"], "rb")
            entities = pickle.load(fp)
            fp.close()

            fp = open(chunk_manifest["tileentities"], "rb")
            tileentities = pickle.load(fp)
            fp.close()

            chunks.append(Chunk2(*chunk_coords, blocks, entities, tileentities))

        return chunks

    def undo(self) -> List[Chunk2]:
        if self._change_index == 0:
            raise Exception("No more changes to undo")
        else:
            self._change_index -= 1
        return self._unserialize_chunks()

    def redo(self) -> List[Chunk2]:
        if self._change_index == (len(self._history) - 1):
            raise Exception("No more changes to redo")
        else:
            self._change_index += 1
        return self._unserialize_chunks()


"""
if __name__ == "__main__":
    hist_manager = ChunkHistoryManager(work_dir="work")
    c00 = Chunk2(0, 0, blocks=numpy.zeros((16, 256, 16)))
    c11 = Chunk2(1, 1, blocks=numpy.ones((16, 256, 16)))
    hist_manager.add_changed_chunks([c00, c11])

    subch00 = c00[0:4,0:4,0:4]
    subch00.blocks = numpy.full(subch00.blocks.shape, 111, subch00.blocks.dtype)
    #c11.blocks[0, 0, 0] = 111

    #c00.entities.append("test")

    #raise Exception(c00.changed)

    hist_manager.add_changed_chunks([c00, c11])

    print(hist_manager.undo())
    print("=" * 32)
    print(hist_manager.undo())
"""

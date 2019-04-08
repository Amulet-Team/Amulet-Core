from __future__ import annotations

from typing import Dict, List, Tuple

from os import makedirs
from os.path import exists, join

from api.chunk import Chunk

_ChunkRecord = Tuple[str, str]


class ChunkHistoryManager:
    def __init__(self, work_dir: str = "."):
        self._history: List[Dict[Tuple[int, int], _ChunkRecord]] = [{}]
        self._change_index: int = 0
        self.work_dir: str = work_dir

    @property
    def change_index(self) -> int:
        return self._change_index

    def add_original_chunk(self, chunk: Chunk):

        self._history[0][(chunk.cx, chunk.cz)] = self.serialize_chunk(chunk, 0)

    def add_changed_chunks(self, chunks: List[Chunk]):
        self._change_index += 1
        change_no = self._change_index
        change_manifest = {}

        if change_no < len(self._history):
            raise NotImplementedError()

        if change_no == 0:
            raise NotImplementedError()

        deleted_chunks = map(
            lambda c: (c.cx, c.cz), filter(lambda c: c.marked_for_deletion, chunks)
        )

        for chunk in chunks:
            change_manifest[(chunk.cx, chunk.cz)] = self.serialize_chunk(
                chunk, change_no
            )

        self._history.append(change_manifest)

        return deleted_chunks

    def serialize_chunk(self, chunk: Chunk, change_no: int) -> _ChunkRecord:
        change_path = join(self.work_dir, str(change_no))

        if not exists(change_path):
            makedirs(change_path, exist_ok=True)

        serialized_chunk = (
            chunk.serialize_chunk(change_path),
            "DELETE" if chunk.marked_for_deletion else "EDIT",
        )

        chunk._changed = False

        return serialized_chunk

    def _unserialize_chunks(self) -> Tuple[List[Chunk], List[Chunk]]:
        edited_chunks = []
        deleted_chunks = []

        for chunk_coords, chunk_manifest in self._history[self._change_index].items():
            chunk = Chunk.unserialize_chunk(chunk_manifest[0])

            if chunk_manifest[1] == "DELETE":
                deleted_chunks.append(chunk)
            else:
                edited_chunks.append(chunk)

        return edited_chunks, deleted_chunks

    def undo(self) -> Tuple[List[Chunk], List[Chunk]]:
        if self._change_index == 0:
            raise Exception("No more changes to undo")
        else:
            self._change_index -= 1
        return self._unserialize_chunks()

    def redo(self) -> Tuple[List[Chunk], List[Chunk]]:
        if self._change_index == (len(self._history) - 1):
            raise Exception("No more changes to redo")
        else:
            self._change_index += 1
        return self._unserialize_chunks()

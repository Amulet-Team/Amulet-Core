from __future__ import annotations

from typing import Dict, List, Tuple

from os import makedirs
from os.path import exists, join

from api.chunk import Chunk

_ChunkRecord = Tuple[str, str]


class ChunkHistoryManager:
    """
    Class to manage changes to chunks along with deletions
    """

    def __init__(self, work_dir: str = "."):
        self._history: List[Dict[Tuple[int, int], _ChunkRecord]] = [{}]
        self._change_index: int = 0
        self.work_dir: str = work_dir

    @property
    def change_index(self) -> int:
        """
        :return: The change index the manager is currently at
        """
        return self._change_index

    def add_original_chunk(self, chunk: Chunk):
        """
        Adds the given chunk to the original history entry
        :param chunk: The chunk in it's original state
        """

        self._history[0][(chunk.cx, chunk.cz)] = self._serialize_chunk(chunk, 0)

    def add_changed_chunks(self, chunks: List[Chunk]):
        """
        Adds the supplied chunks to a new change record

        :param chunks: The chunks that have been changed
        """
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
            change_manifest[(chunk.cx, chunk.cz)] = self._serialize_chunk(
                chunk, change_no
            )

        self._history.append(change_manifest)

        return deleted_chunks

    def _serialize_chunk(self, chunk: Chunk, change_no: int) -> _ChunkRecord:
        """
        Serializes the given ``api.chunk.Chunk`` to disk and returns a tuple containing the path to the chunk file and the type of action performed

        :param chunk: The ``api.chunk.Chunk`` object to serialize
        :param change_no: The change number to serialize the Chunk to
        :return: A tuple containing the file location path and the action type
        """
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
        """
        Unserializes all of chunks at the given chunk record at :attr:`api.history_manager.ChunkHistoryManager.change_index`

        :return: A tuple of a list of the changed chunks. The first index being edited chunks, the second one being chunks that were deleted
        """
        edited_chunks = []
        deleted_chunks = []

        for chunk_manifest in self._history[self._change_index].values():
            chunk = Chunk.unserialize_chunk(chunk_manifest[0])

            if chunk_manifest[1] == "DELETE":
                deleted_chunks.append(chunk)
            else:
                edited_chunks.append(chunk)

        return edited_chunks, deleted_chunks

    def undo(self) -> Tuple[List[Chunk], List[Chunk]]:
        """
        Decrements the internal change index and unserializes the chunks from the last change

        :return: The chunks that were changed as a tuple. The first index being the edited chunks, and the second one being chunks that were deleted
        """
        if self._change_index == 0:
            raise Exception("No more changes to undo")
        else:
            self._change_index -= 1
        return self._unserialize_chunks()

    def redo(self) -> Tuple[List[Chunk], List[Chunk]]:
        """
        Re-increments the internal change index and unserializes the chunks from the next newest change

        :return: The chunks that were changed as a tuple. The first index being the edited chunks, and the second one being chunks that were deleted
        """
        if self._change_index == (len(self._history) - 1):
            raise Exception("No more changes to redo")
        else:
            self._change_index += 1
        return self._unserialize_chunks()

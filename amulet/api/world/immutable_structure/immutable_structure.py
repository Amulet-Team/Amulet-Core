from __future__ import annotations

from ..chunk_world import ChunkWorld
from .void_format_wrapper import VoidFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.data_types import Dimension
import copy


class ImmutableStructure(ChunkWorld):
    """
    This is a special class that exists purely to hold chunk data and serialise it to the disk cache.
    There is no world attached to load or save chunks to.
    This class exists purely to store chunks in when copied from a world.
    The original wrapper is mutable so the chunks must be deep copied from it and dropped into here.
    """

    def __init__(
        self,
        temp_dir: str = None,
    ):

        super().__init__("", VoidFormatWrapper(""), temp_dir)

    def undo(self):
        pass

    def redo(self):
        pass

    def put_chunk(self, chunk: Chunk, dimension: Dimension):
        super().put_chunk(copy.deepcopy(chunk), dimension)
        self.history_manager.create_undo_point()

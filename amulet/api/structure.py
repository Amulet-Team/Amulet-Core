import copy
from typing import Dict, Union, Generator, Tuple, Optional
import itertools

from .selection import Selection, SubSelectionBox
from .world import World, BaseStructure
from .chunk import Chunk
from .block import Block, BlockManager
from .errors import ChunkDoesNotExist
from ..utils.world_utils import Coordinates, block_coords_to_chunk_coords, blocks_slice_to_chunk_slice


class Structure(BaseStructure):
    def __init__(self, chunks: Dict[Coordinates, Chunk], palette: BlockManager, selection: Selection):
        self._chunk_cache = chunks
        self._palette = palette
        self._selection = selection

    @classmethod
    def from_world(cls, world: World, selection: Selection, dimension: int):
        data = {}
        for chunk, _ in world.get_chunk_boxes(selection, dimension):
            if chunk.coordinates not in data:
                data[chunk.coordinates] = copy.deepcopy(chunk)
        return cls(data, world.palette, copy.deepcopy(selection))

    def get_chunk(self, cx: int, cz: int) -> Chunk:
        if (cx, cz) in self._chunk_cache:
            return self._chunk_cache[(cx, cz)]
        else:
            raise ChunkDoesNotExist

    def get_block(self, x: int, y: int, z: int) -> Block:
        cx, cz = block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        chunk = self.get_chunk(cx, cz)
        block = chunk.blocks[offset_x, y, offset_z]
        return self._palette[block]

    def get_chunk_boxes(
        self,
        selection: Optional[Union[Selection, SubSelectionBox]] = None
    ) -> Generator[Tuple[Chunk, SubSelectionBox], None, None]:
        """Given a selection will yield chunks and SubSelectionBoxes into that chunk

        :param selection: Selection or SubSelectionBox into the world
        """
        if selection is None:
            selection = self._selection
        if isinstance(selection, SubSelectionBox):
            selection = Selection([selection])
        selection: Selection
        for box in selection.subboxes:
            first_chunk = block_coords_to_chunk_coords(box.min_x, box.min_z)
            last_chunk = block_coords_to_chunk_coords(box.max_x - 1, box.max_z - 1)
            for chunk_pos in itertools.product(
                    range(first_chunk[0], last_chunk[0] + 1),
                    range(first_chunk[1], last_chunk[1] + 1),
            ):
                try:
                    chunk = self.get_chunk(*chunk_pos)
                except ChunkDoesNotExist:
                    continue

                yield chunk, box

    def get_chunk_slices(
        self,
        selection: Optional[Union[Selection, SubSelectionBox]] = None
    ) -> Generator[Tuple[Chunk, Tuple[slice, slice, slice]], None, None]:
        """Given a selection will yield chunks and slices into that chunk

        :param selection: Selection or SubSelectionBox into the world
        Usage:
        for chunk, slice in world.get_chunk_slices(selection):
            chunk.blocks[slice] = ...
        """
        for chunk, box in self.get_chunk_boxes(selection):
            s_x, s_y, s_z = box.slice
            x_slice_for_chunk = blocks_slice_to_chunk_slice(
                s_x, self.chunk_size[0], chunk.cx
            )
            y_slice_for_chunk = blocks_slice_to_chunk_slice(s_y, self.chunk_size[1], 0)
            z_slice_for_chunk = blocks_slice_to_chunk_slice(
                s_z, self.chunk_size[2], chunk.cz
            )

            yield chunk, (x_slice_for_chunk, y_slice_for_chunk, z_slice_for_chunk)

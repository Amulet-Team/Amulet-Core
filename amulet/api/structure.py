import copy
from typing import Dict, Union, Generator, Tuple, Optional
import itertools
import numpy

from .selection import Selection, SubSelectionBox
from .world import World, BaseStructure
from .chunk import Chunk
from .block import Block, BlockManager
from .errors import ChunkDoesNotExist
from amulet.api.data_types import Coordinates
from ..utils.world_utils import block_coords_to_chunk_coords
from amulet.api.data_types import Dimension


structure_buffer = []


class Structure(BaseStructure):
    def __init__(
        self,
        chunks: Dict[Coordinates, Chunk],
        palette: BlockManager,
        selection: Selection,
        chunk_size: Tuple[int, int, int] = (16, 256, 16),
    ):
        self._chunk_cache = chunks
        self._palette = palette
        self._selection = selection
        self._chunk_size = chunk_size

    @property
    def chunk_size(self) -> Tuple[int, int, int]:
        return self._chunk_size

    @property
    def palette(self) -> BlockManager:
        return self._palette

    @property
    def selection(self) -> Selection:
        return self._selection

    @classmethod
    def from_world(cls, world: World, selection: Selection, dimension: Dimension):
        data = {}
        for chunk, _ in world.get_chunk_boxes(selection, dimension):
            if chunk.coordinates not in data:
                data[chunk.coordinates] = copy.deepcopy(chunk)
        return cls(data, world.palette, copy.deepcopy(selection), world.chunk_size)

    def get_chunk(self, cx: int, cz: int) -> Chunk:
        if (cx, cz) in self._chunk_cache:
            return self._chunk_cache[(cx, cz)]
        else:
            raise ChunkDoesNotExist

    def get_block(self, x: int, y: int, z: int) -> Block:
        cx, cz = block_coords_to_chunk_coords(x, z, chunk_size=self.chunk_size[0])
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        chunk = self.get_chunk(cx, cz)
        block = chunk.blocks[offset_x, y, offset_z]
        return self._palette[block]

    def get_chunk_boxes(
        self, selection: Optional[Union[Selection, SubSelectionBox]] = None
    ) -> Generator[Tuple[Chunk, SubSelectionBox], None, None]:
        """Given a selection will yield chunks and SubSelectionBoxes into that chunk

        :param selection: Selection or SubSelectionBox into the world
        """
        if selection is None:
            selection = self._selection
        else:
            if isinstance(selection, SubSelectionBox):
                selection = Selection([selection])
            # TODO: handle the fact the the selection is not at the origin
            selection = self.selection.intersection(selection)
        selection: Selection
        for box in selection.subboxes:
            first_chunk = block_coords_to_chunk_coords(box.min_x, box.min_z, chunk_size=self.chunk_size[0])
            last_chunk = block_coords_to_chunk_coords(box.max_x - 1, box.max_z - 1, chunk_size=self.chunk_size[0])
            for cx, cz in itertools.product(
                range(first_chunk[0], last_chunk[0] + 1),
                range(first_chunk[1], last_chunk[1] + 1),
            ):
                try:
                    chunk = self.get_chunk(cx, cz)
                except ChunkDoesNotExist:
                    continue

                yield chunk, box.intersection(self._chunk_box(cx, cz))

    def get_chunk_slices(
        self, selection: Optional[Union[Selection, SubSelectionBox]] = None
    ) -> Generator[
        Tuple[Chunk, Tuple[slice, slice, slice], SubSelectionBox], None, None
    ]:
        """Given a selection will yield chunks and slices into that chunk

        :param selection: Selection or SubSelectionBox into the world
        Usage:
        for chunk, slice in world.get_chunk_slices(selection):
            chunk.blocks[slice] = ...
        """
        for chunk, box in self.get_chunk_boxes(selection):
            slices = box.chunk_slice(chunk.cx, chunk.cz, self.chunk_size[0])
            yield chunk, slices, box

    def get_moved_chunk_slices(
        self,
        destination_origin: Tuple[int, int, int],
        selection: Optional[Union[Selection, SubSelectionBox]] = None,
        destination_chunk_shape: Optional[Tuple[int, int, int]] = None,
    ) -> Generator[
        Tuple[
            Chunk,
            Tuple[slice, slice, slice],
            SubSelectionBox,
            Tuple[int, int],
            Tuple[slice, slice, slice],
            SubSelectionBox,
        ],
        None,
        None,
    ]:
        """Iterate over a selection and return slices into the source object and destination object
        given the origin of the destination. When copying a selection to a new area the slices will
        only be equal if the offset is a multiple of the chunk size. This will rarely be the case
        so the slices need to be split up into parts that intersect a chunk in the source and destination.
        :param destination_origin: The location where the minimum point of self.selection will end up
        :param selection: An optional selection. The overlap of this and self.selection will be used
        :param destination_chunk_shape: the chunk shape of the destination object (defaults to self.chunk_size)
        :return:
        """
        if destination_chunk_shape is None:
            destination_chunk_shape = self.chunk_size

        if selection is None:
            selection = self.selection
        else:
            # TODO: handle the fact the the selection is not at the origin
            selection = self.selection.intersection(selection)
        # the offset from self.selection to the destination location
        offset = numpy.subtract(destination_origin, self.selection.min, dtype=numpy.int)
        for chunk, box in self.get_chunk_boxes(selection):
            dst_full_box = SubSelectionBox(offset + box.min, offset + box.max,)

            first_chunk = block_coords_to_chunk_coords(
                dst_full_box.min_x,
                dst_full_box.min_z,
                chunk_size=destination_chunk_shape[0]
            )
            last_chunk = block_coords_to_chunk_coords(
                dst_full_box.max_x - 1,
                dst_full_box.max_z - 1,
                chunk_size=destination_chunk_shape[0]
            )
            for cx, cz in itertools.product(
                range(first_chunk[0], last_chunk[0] + 1),
                range(first_chunk[1], last_chunk[1] + 1),
            ):
                chunk_box = self._chunk_box(cx, cz, destination_chunk_shape)
                dst_box = chunk_box.intersection(dst_full_box)
                src_box = SubSelectionBox(-offset + dst_box.min, -offset + dst_box.max)
                src_slices = src_box.chunk_slice(chunk.cx, chunk.cz, self.chunk_size[0])
                dst_slices = dst_box.chunk_slice(cx, cz, self.chunk_size[0])
                yield chunk, src_slices, src_box, (cx, cz), dst_slices, dst_box

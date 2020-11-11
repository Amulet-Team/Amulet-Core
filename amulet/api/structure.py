import copy
from typing import Dict, Union, Generator, Tuple, Optional, List
import itertools
import numpy

from .selection import SelectionGroup, SelectionBox
from .base_structure import BaseStructure
from .world import World
from .chunk import Chunk
from .block import Block
from amulet.api.registry import BlockManager
from .errors import ChunkDoesNotExist
from amulet.api.data_types import ChunkCoordinates, Dimension, FloatTriplet
from ..utils.world_utils import block_coords_to_chunk_coords
from amulet.utils.matrix import transform_matrix


class StructureCache:
    """A class for storing and accessing structure objects"""

    def __init__(self):
        self._structure_buffer: List[Structure] = []

    def add_structure(self, structure: "Structure"):
        """Add a structure to the cache"""
        assert isinstance(
            structure, Structure
        ), "structure given is not a Structure instance"
        self._structure_buffer.append(structure)

    def get_structure(self, index=-1) -> "Structure":
        """Get a structure from the cache. Default last."""
        return self._structure_buffer[index]

    def pop_structure(self, index=-1) -> "Structure":
        """Get and remove a structure from the cache. Default last."""
        return self._structure_buffer.pop(index)

    def __len__(self) -> int:
        """Get the number of structures in the cache"""
        return len(self._structure_buffer)

    def clear(self):
        """Empty the cache."""
        self._structure_buffer.clear()


structure_cache = StructureCache()


class Structure(BaseStructure):
    def __init__(
        self,
        chunks: Dict[ChunkCoordinates, Chunk],
        palette: BlockManager,
        selection: SelectionGroup,
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
    def selection(self) -> SelectionGroup:
        return self._selection

    @classmethod
    def from_world(cls, world: World, selection: SelectionGroup, dimension: Dimension):
        data = {}
        block_palette = BlockManager()
        for chunk, _ in world.get_chunk_boxes(selection, dimension):
            if chunk.coordinates not in data:
                data[chunk.coordinates] = chunk = copy.deepcopy(chunk)
                chunk.block_palette = block_palette
        return cls(data, block_palette, copy.deepcopy(selection), world.chunk_size)

    def get_chunk(self, cx: int, cz: int) -> Chunk:
        if (cx, cz) in self._chunk_cache:
            return self._chunk_cache[(cx, cz)]
        else:
            raise ChunkDoesNotExist

    def get_block(self, x: int, y: int, z: int) -> Block:
        cx, cz = block_coords_to_chunk_coords(x, z, chunk_size=self.sub_chunk_size)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        chunk = self.get_chunk(cx, cz)
        block = chunk.blocks[offset_x, y, offset_z]
        return self._palette[block]

    def get_chunk_boxes(
        self,
        selection: Optional[Union[SelectionGroup, SelectionBox]] = None,
        generate_non_exists: bool = False,
    ) -> Generator[Tuple[Chunk, SelectionBox], None, None]:
        """Given a selection will yield chunks and SubSelectionBoxes into that chunk

        :param selection: SelectionGroup or SelectionBox into the world
        :param generate_non_exists: Generate empty read-only chunks if the chunk does not exist.
        """
        if selection is None:
            selection = self._selection
        else:
            if isinstance(selection, SelectionBox):
                selection = SelectionGroup([selection])
            # TODO: handle the fact the the selection is not at the origin
            selection = self.selection.intersection(selection)
        selection: SelectionGroup
        for box in selection.selection_boxes:
            first_chunk = block_coords_to_chunk_coords(
                box.min_x, box.min_z, chunk_size=self.sub_chunk_size
            )
            last_chunk = block_coords_to_chunk_coords(
                box.max_x - 1, box.max_z - 1, chunk_size=self.sub_chunk_size
            )
            for cx, cz in itertools.product(
                range(first_chunk[0], last_chunk[0] + 1),
                range(first_chunk[1], last_chunk[1] + 1),
            ):
                try:
                    chunk = self.get_chunk(cx, cz)
                except ChunkDoesNotExist:
                    if generate_non_exists:
                        chunk = Chunk(cx, cz)
                        chunk.block_palette = self.palette
                    else:
                        continue

                yield chunk, box.intersection(self._chunk_box(cx, cz))

    def get_chunk_slices(
        self, selection: Optional[Union[SelectionGroup, SelectionBox]] = None
    ) -> Generator[Tuple[Chunk, Tuple[slice, slice, slice], SelectionBox], None, None]:
        """Given a selection will yield chunks and slices into that chunk

        :param selection: SelectionGroup or SelectionBox into the world
        Usage:
        for chunk, slice in world.get_chunk_slices(selection):
            chunk.blocks[slice] = ...
        """
        for chunk, box in self.get_chunk_boxes(selection):
            slices = box.chunk_slice(chunk.cx, chunk.cz, self.sub_chunk_size)
            yield chunk, slices, box

    def get_moved_chunk_slices(
        self,
        destination_origin: Tuple[int, int, int],
        selection: Optional[Union[SelectionGroup, SelectionBox]] = None,
        destination_chunk_shape: Optional[Tuple[int, int, int]] = None,
        generate_non_exists: bool = False,
    ) -> Generator[
        Tuple[
            Chunk,
            Tuple[slice, slice, slice],
            SelectionBox,
            ChunkCoordinates,
            Tuple[slice, slice, slice],
            SelectionBox,
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
        :param generate_non_exists: Generate empty read-only chunks if the chunk does not exist.
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
        for chunk, box in self.get_chunk_boxes(selection, generate_non_exists):
            dst_full_box = SelectionBox(
                offset + box.min,
                offset + box.max,
            )

            first_chunk = block_coords_to_chunk_coords(
                dst_full_box.min_x,
                dst_full_box.min_z,
                chunk_size=destination_chunk_shape[0],
            )
            last_chunk = block_coords_to_chunk_coords(
                dst_full_box.max_x - 1,
                dst_full_box.max_z - 1,
                chunk_size=destination_chunk_shape[0],
            )
            for cx, cz in itertools.product(
                range(first_chunk[0], last_chunk[0] + 1),
                range(first_chunk[1], last_chunk[1] + 1),
            ):
                chunk_box = self._chunk_box(cx, cz, destination_chunk_shape)
                dst_box = chunk_box.intersection(dst_full_box)
                src_box = SelectionBox(-offset + dst_box.min, -offset + dst_box.max)
                src_slices = src_box.chunk_slice(
                    chunk.cx, chunk.cz, self.sub_chunk_size
                )
                dst_slices = dst_box.chunk_slice(cx, cz, self.sub_chunk_size)
                yield chunk, src_slices, src_box, (cx, cz), dst_slices, dst_box

    def transform(self, scale: FloatTriplet, rotation: FloatTriplet) -> "Structure":
        """
        creates a new transformed Structure class.
        :param scale: scale factor multiplier in the x, y and z directions
        :param rotation: rotation in degrees for pitch (y), yaw (z) and roll (x)
        :return:
        """
        iter_ = self.transform_iter(scale, rotation)
        try:
            while True:
                next(iter_)
        except StopIteration as e:
            return e.value

    def transform_iter(
        self, scale: FloatTriplet, rotation: FloatTriplet
    ) -> Generator[int, None, "Structure"]:
        """
        creates a new transformed Structure class.
        :param scale: scale factor multiplier in the x, y and z directions
        :param rotation: rotation in degrees for pitch (y), yaw (z) and roll (x)
        :return:
        """
        block_palette = copy.deepcopy(self.palette)
        rotation_radians = -numpy.flip(numpy.radians(rotation))
        selection = self.selection.transform(scale, rotation_radians)
        transform = transform_matrix((0, 0, 0), scale, rotation_radians, "zyx")
        inverse_transform = numpy.linalg.inv(transform)

        chunks: Dict[ChunkCoordinates, Chunk] = {}

        volume = sum([box.volume for box in selection.selection_boxes])
        index = 0

        # TODO: find a way to do this without doing it block by block
        for box in selection.selection_boxes:
            coords = list(box.blocks())
            coords_array = numpy.ones((len(coords), 4), dtype=numpy.float)
            coords_array[:, :3] = coords
            coords_array[:, :3] += 0.5
            original_coords = (
                numpy.floor(numpy.matmul(inverse_transform, coords_array.T))
                .astype(int)
                .T[:, :3]
            )
            for (x, y, z), (ox, oy, oz) in zip(coords, original_coords):
                cx, cz = chunk_key = (x >> 4, z >> 4)
                if chunk_key in chunks:
                    chunk = chunks[chunk_key]
                else:
                    chunk = chunks[chunk_key] = Chunk(cx, cz)
                    chunk.block_palette = block_palette
                try:
                    chunk.blocks[x % 16, y, z % 16] = self.get_chunk(
                        ox >> 4, oz >> 4
                    ).blocks[ox % 16, oy, oz % 16]
                except ChunkDoesNotExist:
                    pass
                yield index / volume
                index += 1

        return Structure(chunks, block_palette, selection, self.chunk_size)

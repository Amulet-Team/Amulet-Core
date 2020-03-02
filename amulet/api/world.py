from __future__ import annotations

from copy import deepcopy
import itertools
import os
import shutil
from typing import Union, Generator, Dict, Optional, Tuple, List, Callable

from amulet import log
from .block import Block, BlockManager
from .errors import ChunkDoesNotExist, ChunkLoadError, LevelDoesNotExist
from .history_manager import ChunkHistoryManager
from .chunk import Chunk, SubChunk
from .operation import Operation
from .selection import SelectionBox
from .paths import get_temp_dir
from ..utils.world_utils import (
    block_coords_to_chunk_coords,
    blocks_slice_to_chunk_slice,
    Coordinates,
    DimensionCoordinates,
    entity_position_to_chunk_coordinates,
    get_entity_coordinates,
)
from ..world_interface.formats import Format

from . import operation

ChunkCache = Dict[DimensionCoordinates, Union[Chunk, None]]


class World:
    """
    Class that handles world editing of any world format via an separate and flexible data format
    """

    def __init__(self, directory: str, world_wrapper: Format, temp_dir: str = None):
        self._directory = directory
        if temp_dir is None:
            self._temp_directory = get_temp_dir(self._directory)
        else:
            self._temp_directory = temp_dir

        self.world_wrapper = world_wrapper
        self.world_wrapper.open()

        self.palette = BlockManager()
        self.palette.get_add_block(
            Block(namespace="universal_minecraft", base_name="air")
        )  # ensure that index 0 is always air

        self._chunk_cache: ChunkCache = {}
        shutil.rmtree(self._temp_directory, ignore_errors=True)
        self._chunk_history_manager = ChunkHistoryManager(
            os.path.join(self._temp_directory, "chunks")
        )

    @property
    def world_path(self) -> str:
        """The directory where the world is located"""
        return self._directory

    @property
    def changed(self) -> bool:
        """Has any data been modified but not saved to disk"""
        return self.world_wrapper.changed or any(
            chunk is None or chunk.changed for chunk in self._chunk_cache.values()
        )

    @property
    def chunk_size(self) -> Tuple[int, int, int]:
        return self.world_wrapper.chunk_size

    def save(
        self,
        wrapper: Format = None,
        progress_callback: Callable[[int, int], None] = None,
    ):
        """Save the world using the given wrapper.
        Leave as None to save back to the input wrapper.
        Optional progress callback to let the calling program know the progress. Input format chunk_index, chunk_count"""
        chunk_index = 0
        chunk_count = len(self._chunk_cache)

        def update_progress():
            nonlocal chunk_index
            chunk_index += 1
            if progress_callback is not None:
                progress_callback(chunk_index, chunk_count)

        if wrapper is None:
            wrapper = self.world_wrapper

        dimstr2dim = self.world_wrapper.dimensions
        dim2dimstr = {val: key for key, val in dimstr2dim.items()}
        output_dimension_map = wrapper.dimensions

        # perhaps make this check if the directory is the same rather than if the class is the same
        save_as = wrapper is not self.world_wrapper
        if save_as:
            # The input wrapper is not the same as the loading wrapper (save-as)
            # iterate through every chunk in the input world and save them to the wrapper
            log.info(
                f"Converting world {self.world_wrapper.world_path} to world {wrapper.world_path}"
            )
            wrapper.translation_manager = (
                self.world_wrapper.translation_manager
            )  # TODO: this might cause issues in the future
            for dimension in self.world_wrapper.dimensions.values():
                chunk_count += len(list(self.world_wrapper.all_chunk_coords(dimension)))

            for dimension_name, dimension in self.world_wrapper.dimensions.items():
                try:
                    if dimension_name not in output_dimension_map:
                        continue
                    output_dimension = output_dimension_map[dimension_name]
                    for cx, cz in self.world_wrapper.all_chunk_coords(dimension):
                        log.info(f"Converting chunk {dimension_name} {cx}, {cz}")
                        try:
                            chunk = self.world_wrapper.load_chunk(
                                cx, cz, self.palette, dimension
                            )
                            wrapper.commit_chunk(chunk, self.palette, output_dimension)
                        except ChunkLoadError:
                            log.info(f"Error loading chunk {cx} {cz}", exc_info=True)
                        update_progress()
                        if not chunk_index % 10000:
                            wrapper.save()
                            self.world_wrapper.unload()
                            wrapper.unload()
                except LevelDoesNotExist:
                    continue

        for (dimension, cx, cz), chunk in self._chunk_cache.items():
            dimension_out = output_dimension_map.get(dim2dimstr.get(dimension))
            if dimension_out is None:
                continue
            if chunk is None:
                wrapper.delete_chunk(cx, cz, dimension_out)
            elif chunk.changed:
                wrapper.commit_chunk(deepcopy(chunk), self.palette, dimension_out)
            update_progress()
            if not chunk_index % 10000:
                wrapper.save()
                wrapper.unload()
        log.info(f"Saving changes to world {wrapper.world_path}")
        wrapper.save()
        log.info(f"Finished saving changes to world {wrapper.world_path}")

    def close(self):
        """Close the attached world and remove temporary files
        Use changed method to check if there are any changes that should be saved before closing."""
        # TODO: add "unsaved changes" check before exit
        shutil.rmtree(self._temp_directory, ignore_errors=True)
        self.world_wrapper.close()

    def unload(self, safe_area: Optional[Tuple[int, int, int, int, int]] = None):
        """Unload all chunks not in the safe area
        Safe area format: dimension, min chunk X|Z, max chunk X|Z"""
        unload_chunks = []
        if safe_area is None:
            for key in self._chunk_cache.keys():
                unload_chunks.append(key)
        else:
            dimension, minx, minz, maxx, maxz = safe_area
            for (cd, cx, cz), chunk in self._chunk_cache.items():
                if not (cd == dimension and minx <= cx <= maxx and minz <= cz <= maxz):
                    unload_chunks.append((cd, cx, cz))
        for chunk_key in unload_chunks:
            del self._chunk_cache[chunk_key]
        self.world_wrapper.unload()

    def get_chunk(self, cx: int, cz: int, dimension: int = 0) -> Chunk:
        """
        Gets the chunk data of the specified chunk coordinates.
        If the chunk does not exist ChunkDoesNotExist is raised.
        If some other error occurs then ChunkLoadError is raised (this error will also catch ChunkDoesNotExist)

        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :param dimension: The dimension to get the chunk from
        :return: The blocks, entities, and tile entities in the chunk
        """
        chunk_key = (dimension, cx, cz)
        if chunk_key in self._chunk_cache:
            chunk = self._chunk_cache[(dimension, cx, cz)]
        elif chunk_key in self._chunk_history_manager:
            chunk = self._chunk_cache[
                (dimension, cx, cz)
            ] = self._chunk_history_manager.get_current(*chunk_key)
        else:
            chunk = self.world_wrapper.load_chunk(cx, cz, self.palette, dimension)
            self._chunk_cache[(dimension, cx, cz)] = chunk
            self._chunk_history_manager.add_original_chunk(chunk, dimension)

        if chunk is None:
            raise ChunkDoesNotExist(f"Chunk ({cx},{cz}) has been deleted")

        return chunk

    def put_chunk(self, chunk: Chunk, dimension: int = 0):
        """Add a chunk to the universal world database"""
        chunk.changed = True
        self._chunk_cache[(dimension, chunk.cx, chunk.cz)] = chunk

    def delete_chunk(self, cx: int, cz: int, dimension: int = 0):
        """Delete a chunk from the universal world database"""
        self._chunk_cache[(dimension, cx, cz)] = None

    def get_block(self, x: int, y: int, z: int) -> Block:
        """
        Gets the blockstate at the specified coordinates

        :param x: The X coordinate of the desired block
        :param y: The Y coordinate of the desired block
        :param z: The Z coordinate of the desired block
        :return: The blockstate name as a string
        """
        # TODO: move this logic into the chunk class and have this method call that
        if not (0 <= y <= 255):
            raise IndexError("The supplied Y coordinate must be between 0 and 255")

        cx, cz = block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        chunk = self.get_chunk(cx, cz)
        block = chunk[offset_x, y, offset_z].blocks
        return self.palette[block]

    def get_sub_chunks(
        self, *args: Union[slice, int]
    ) -> Generator[SubChunk, None, None]:
        # TODO: move this logic into the chunk class and have this method call that
        length = len(args)
        if length == 3:
            s_x, s_y, s_z = args
        elif length == 6:
            s_x, s_y, s_z = (
                slice(args[0], args[3]),
                slice(args[1], args[4]),
                slice(args[2], args[5]),
            )
        elif length == 9:
            s_x, s_y, s_z = (
                slice(args[0], args[3], args[6]),
                slice(args[1], args[4], args[7]),
                slice(args[2], args[5], args[8]),
            )
        else:
            raise IndexError(
                "Length of parameters to 'get_sub_chunks' should be 3, 6 or 9"
            )

        if not (
            isinstance(s_x, slice) and isinstance(s_y, slice) and isinstance(s_z, slice)
        ):
            raise IndexError("The function 'get_sub_chunks' gets only slices")

        first_chunk = block_coords_to_chunk_coords(s_x.start, s_z.start)
        last_chunk = block_coords_to_chunk_coords(s_x.stop, s_z.stop)
        for chunk_pos in itertools.product(
            range(first_chunk[0], last_chunk[0] + 1),
            range(first_chunk[1], last_chunk[1] + 1),
        ):
            x_slice_for_chunk = (
                blocks_slice_to_chunk_slice(s_x)
                if chunk_pos == first_chunk
                else slice(None)
            )
            z_slice_for_chunk = (
                blocks_slice_to_chunk_slice(s_z)
                if chunk_pos == last_chunk
                else slice(None)
            )
            try:
                chunk = self.get_chunk(*chunk_pos)
            except ChunkDoesNotExist:
                continue
            if chunk is None:
                continue
            yield chunk[x_slice_for_chunk, s_y, z_slice_for_chunk]

    def get_entities_in_box(
        self, box: "SelectionBox"
    ) -> Generator[Tuple[Coordinates, List[object]], None, None]:
        # TODO: some of this logic can probably be moved the chunk class and have this method call that
        # TODO: update this to use the newer entity API
        out_of_place_entities = []
        entity_map: Dict[Tuple[int, int], List[List[object]]] = {}
        for subbox in box.subboxes():
            for subchunk in self.get_sub_chunks(*subbox.to_slice()):
                chunk_coords = subchunk.parent_coordinates
                chunk = self.get_chunk(*chunk_coords)
                entities = chunk.entities

                in_box = list(
                    filter(lambda e: get_entity_coordinates(e) in subbox, entities)
                )
                not_in_box = filter(
                    lambda e: get_entity_coordinates(e) not in subbox, entities
                )

                in_box_copy = deepcopy(in_box)

                entity_map[chunk_coords] = [
                    not_in_box,
                    in_box,
                ]  # First index is the list of entities not in the box, the second is for ones that are

                yield chunk_coords, in_box_copy

                if (
                    in_box != in_box_copy
                ):  # If an entity has been changed, update the dictionary entry
                    entity_map[chunk_coords][1] = in_box_copy
                else:  # Delete the entry otherwise
                    del entity_map[chunk_coords]

        for chunk_coords, entity_list_list in entity_map.items():
            chunk = self.get_chunk(*chunk_coords)
            in_place_entities = list(
                filter(
                    lambda e: chunk_coords
                    == entity_position_to_chunk_coordinates(get_entity_coordinates(e)),
                    entity_list_list[1],
                )
            )
            out_of_place = filter(
                lambda e: chunk_coords
                != entity_position_to_chunk_coordinates(get_entity_coordinates(e)),
                entity_list_list[1],
            )

            chunk.entities = in_place_entities + list(entity_list_list[0])

            if out_of_place:
                out_of_place_entities.extend(out_of_place)

        if out_of_place_entities:
            self.add_entities(out_of_place_entities)

    def add_entities(self, entities):
        proper_entity_chunks = map(
            lambda e: (
                entity_position_to_chunk_coordinates(get_entity_coordinates(e)),
                e,
            ),
            entities,
        )
        accumulated_entities: Dict[Tuple[int, int], List[object]] = {}

        for chunk_coord, ent in proper_entity_chunks:
            if chunk_coord in accumulated_entities:
                accumulated_entities[chunk_coord].append(ent)
            else:
                accumulated_entities[chunk_coord] = [ent]

        for chunk_coord, ents in accumulated_entities.items():
            chunk = self.get_chunk(*chunk_coord)

            chunk.entities += ents

    def delete_entities(self, entities):
        chunk_entity_pairs = map(
            lambda e: (
                entity_position_to_chunk_coordinates(get_entity_coordinates(e)),
                e,
            ),
            entities,
        )

        for chunk_coord, ent in chunk_entity_pairs:
            chunk = self.get_chunk(*chunk_coord)
            entities = chunk.entities
            entities.remove(ent)
            chunk.entities = entities

    def run_operation(self, operation_instance: Operation) -> None:
        operation_instance.run_operation(self)
        self._chunk_history_manager.create_undo_point(self._chunk_cache)

    def run_operation_from_operation_name(
        self, operation_name: str, *args
    ) -> Optional[Exception]:
        operation_instance = operation.OPERATIONS[operation_name](*args)

        e = None
        try:
            self.run_operation(operation_instance)
        except Exception as ex:
            raise ex

        self._chunk_history_manager.create_undo_point(self._chunk_cache)
        return e

    def undo(self):
        """
        Undoes the last set of changes to the world
        """
        self._chunk_history_manager.undo(self._chunk_cache)

    def redo(self):
        """
        Redoes the last set of changes to the world
        """
        self._chunk_history_manager.redo(self._chunk_cache)

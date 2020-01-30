from __future__ import annotations

from copy import deepcopy
import itertools
import os
import shutil
from typing import Union, Generator, Dict, Optional, Tuple, List, Callable

from .block import Block, BlockManager
from .errors import ChunkDoesNotExist, ChunkLoadError
from .history_manager import ChunkHistoryManager
from .chunk import Chunk, SubChunk
from .operation import Operation
from .paths import get_temp_dir
from ..utils.world_utils import (
    block_coords_to_chunk_coords,
    blocks_slice_to_chunk_slice,
    Coordinates,
    entity_position_to_chunk_coordinates,
    get_entity_coordinates,
)
from ..world_interface.formats import Format

from . import operation


class World:
    """
    Class that handles world editing of any world format via an separate and flexible data format
    """

    def __init__(self, directory: str, world_wrapper: Format):
        self._directory = directory
        self.world_wrapper = world_wrapper
        self.world_wrapper.open()
        self.palette = BlockManager()
        self.palette.get_add_block(
            Block(namespace="universal_minecraft", base_name="air")
        )  # ensure that index 0 is always air
        self.chunk_cache: Dict[Coordinates, Chunk] = {}
        shutil.rmtree(get_temp_dir(self._directory), ignore_errors=True)
        self.history_manager = ChunkHistoryManager(get_temp_dir(self._directory))
        self._deleted_chunks = set()

    def save(self, wrapper: Format = None, progress_callback: Callable[[int, int], None] = None):
        """Save the world using the given wrapper.
        Leave as None to save back to the input wrapper.
        Optional progress callback to let the calling program know the progress. Input format chunk_index, chunk_count"""
        chunk_index = 0
        chunk_count = len(self.chunk_cache.values()) + len(self._deleted_chunks)

        def update_progress():
            nonlocal chunk_index
            chunk_index += 1
            if progress_callback is not None:
                progress_callback(chunk_index, chunk_count)

        if wrapper is None:
            wrapper = self.world_wrapper

        # perhaps make this check if the directory is the same rather than if the class is the same
        save_as = wrapper is not self.world_wrapper
        if save_as:
            # The input wrapper is not the same as the loading wrapper (save-as)
            # iterate through every chunk in the input world and the unsaved modified chunks (taking preference for the latter)
            # and save them to the wrapper
            wrapper.translation_manager = self.world_wrapper.translation_manager  # TODO: this might cause issues in the future
            chunk_count += len(list(self.world_wrapper.all_chunk_coords()))

            for cx, cz in self.world_wrapper.all_chunk_coords():
                print(cx, cz)
                try:
                    chunk = self.world_wrapper.load_chunk(cx, cz, self.palette)
                    wrapper.save_chunk(chunk, self.palette)
                except ChunkLoadError:
                    pass
                update_progress()

            for chunk in self.chunk_cache.values():
                if chunk.changed:
                    wrapper.save_chunk(deepcopy(chunk), self.palette)
                update_progress()
            for (cx, cz) in self._deleted_chunks:
                wrapper.delete_chunk(cx, cz)
                update_progress()
            wrapper.save()
        else:
            # The input wrapper is the normal wrapper so just save the modified chunks back
            for (cx, cz) in self._deleted_chunks:
                self.world_wrapper.delete_chunk(cx, cz)
                update_progress()
            self._deleted_chunks.clear()
            for chunk in self.chunk_cache.values():
                if chunk.changed:
                    self.world_wrapper.save_chunk(deepcopy(chunk), self.palette)
                update_progress()
            self.world_wrapper.save()
            # TODO check and flesh this out a bit

    def close(self):
        # TODO: add "unsaved changes" check before exit
        shutil.rmtree(get_temp_dir(self._directory), ignore_errors=True)
        self.world_wrapper.close()

    def get_chunk(self, cx: int, cz: int) -> Chunk:
        """
        Gets the chunk data of the specified chunk coordinates.
        If the chunk does not exist ChunkDoesNotExist is raised.
        If some other error occurs then ChunkLoadError is raised (this error will also catch ChunkDoesNotExist)

        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :return: The blocks, entities, and tile entities in the chunk
        """
        if (cx, cz) in self.chunk_cache:
            return self.chunk_cache[(cx, cz)]

        chunk = self.world_wrapper.load_chunk(cx, cz, self.palette)
        self.chunk_cache[(cx, cz)] = chunk
        self.history_manager.add_original_chunk(chunk)
        return chunk

    def get_block(self, x: int, y: int, z: int) -> Block:
        """
        Gets the blockstate at the specified coordinates

        :param x: The X coordinate of the desired block
        :param y: The Y coordinate of the desired block
        :param z: The Z coordinate of the desired block
        :return: The blockstate name as a string
        """
        if not (0 <= y <= 255):
            raise IndexError("The supplied Y coordinate must be between 0 and 255")

        cx, cz = block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz

        if (cx, cz) in self._deleted_chunks:
            raise ChunkDoesNotExist(f"Chunk ({cx},{cz}) has been deleted")

        chunk = self.get_chunk(cx, cz)
        block = chunk[offset_x, y, offset_z].blocks
        return self.palette[block]

    def get_sub_chunks(
        self, *args: Union[slice, int], include_deleted_chunks=False
    ) -> Generator[SubChunk, None, None]:
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
            chunk = self.get_chunk(*chunk_pos)
            if not include_deleted_chunks and (
                chunk.marked_for_deletion or chunk_pos in self._deleted_chunks
            ):
                continue
            yield chunk[x_slice_for_chunk, s_y, z_slice_for_chunk]

    def get_entities_in_box(
        self, box: "SelectionBox"
    ) -> Generator[Tuple[Coordinates, List[object]], None, None]:

        out_of_place_entities = []
        entity_map: Dict[Tuple[int, int], List[List[object]]] = {}
        for subbox in box.subboxes():
            for subchunk in self.get_sub_chunks(*subbox.to_slice()):
                chunk_coords = subchunk.parent_coordinates
                chunk = self.chunk_cache[chunk_coords]
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
            chunk = self.chunk_cache[chunk_coords]
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
            chunk = self.chunk_cache[chunk_coord]

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
            chunk = self.chunk_cache[chunk_coord]
            entities = chunk.entities
            entities.remove(ent)
            chunk.entities = entities

    def run_operation_from_operation_name(
        self, operation_name: str, *args
    ) -> Optional[Exception]:
        operation_instance = operation.OPERATIONS[operation_name](*args)

        try:
            self.run_operation(operation_instance)
        except Exception as e:
            self._revert_all_chunks()
            return e

        changed_chunks = [chunk for chunk in self.chunk_cache.values() if chunk.changed]

        deleted_chunks = self.history_manager.add_changed_chunks(changed_chunks)
        for ch in deleted_chunks:
            self._deleted_chunks.add(ch)

    def _revert_all_chunks(self):
        for chunk_pos, chunk in self.chunk_cache.items():
            if chunk.previous_unsaved_state is None:
                continue

            self.chunk_cache[chunk_pos] = chunk.previous_unsaved_state

    def _save_to_undo(self):
        for chunk in self.chunk_cache.values():
            if chunk.previous_unsaved_state is None:
                continue

            chunk.previous_unsaved_state.save_to_file(
                os.path.join(
                    get_temp_dir(self._directory),
                    f"Operation_{self.history_manager.undo_stack.size()}",
                )
            )
            chunk.previous_unsaved_state = None

    def undo(self):
        """
        Undoes the last set of changes to the world
        """
        previous_edited_chunks, deleted_chunks = self.history_manager.undo()

        for chunk_obj in previous_edited_chunks:
            chunk_coords = (chunk_obj.cx, chunk_obj.cz)
            if chunk_coords in self._deleted_chunks:
                self._deleted_chunks.remove(chunk_coords)
            self.chunk_cache[chunk_coords] = chunk_obj

        for deleted_chunk in deleted_chunks:
            chunk_coords = (deleted_chunk.cx, deleted_chunk.cz)
            self._deleted_chunks.add(chunk_coords)
            del self.chunk_cache[chunk_coords]

    def redo(self):
        """
        Redoes the last set of changes to the world
        """
        next_edited_chunks, deleted_chunks = self.history_manager.redo()

        for chunk_obj in next_edited_chunks:
            chunk_coords = (chunk_obj.cx, chunk_obj.cz)
            if chunk_coords in self._deleted_chunks:
                self._deleted_chunks.remove(chunk_coords)
            self.chunk_cache[chunk_coords] = chunk_obj

        for deleted_chunk in deleted_chunks:
            chunk_coords = (deleted_chunk.cx, deleted_chunk.cz)
            self._deleted_chunks.add(chunk_coords)
            del self.chunk_cache[chunk_coords]

    def run_operation(self, operation_instance: Operation) -> None:
        operation_instance.run_operation(self)

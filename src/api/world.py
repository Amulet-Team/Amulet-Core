from __future__ import annotations

import itertools
import os
import shutil
from typing import Union, Generator, Dict, Optional
from importlib import import_module

import numpy

from api.history import HistoryManager
from api.chunk import Chunk, SubChunk
from api.operation import Operation
from api.paths import get_temp_dir
from utils.world_utils import (
    block_coords_to_chunk_coords, blocks_slice_to_chunk_slice, Coordinates
)


class WorldFormat:
    """
    Base class for World objects
    """

    mapping_handler: numpy.ndarray = None

    @classmethod
    def load(cls, directory: str, definitions) -> World:
        """
        Loads the Minecraft world contained in the given directory with the supplied definitions

        :param directory: The directory of the world to load
        :param definitions: The definitions to load the world with
        :return: The loaded world in a `World` object
        """
        raise NotImplementedError()

    def get_blocks(self, cx: int, cz: int) -> numpy.ndarray:
        raise NotImplementedError()

    @classmethod
    def from_unified_format(cls, unified: World) -> WorldFormat:
        """
        Converts the passed object to the specific implementation

        :param unified: The object to convert
        :return object: The result of the conversion, None if not successful
        """
        raise NotImplementedError()

    def save(self) -> None:
        """
        Saves the current WorldFormat to disk
        """
        raise NotImplementedError()


class World:
    """
    Class that handles world editing of any world format via an separate and flexible data format
    """

    def __init__(self, directory: str, root_tag, wrapper: WorldFormat):
        self._directory = directory
        shutil.rmtree(get_temp_dir(self._directory), ignore_errors=True)
        self._root_tag = root_tag
        self._wrapper = wrapper
        self.blocks_cache: Dict[Coordinates, Chunk] = {}
        self.history_manager = HistoryManager()

    def exit(self):
        # TODO: add "unsaved changes" check before exit
        shutil.rmtree(get_temp_dir(self._directory), ignore_errors=True)

    @property
    def block_definitions(self) -> numpy.ndarray:
        return self._wrapper.mapping_handler

    def get_chunk(self, cx: int, cz: int) -> Chunk:
        """
        Gets the chunk data of the specified chunk coordinates

        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :return: The blocks, entities, and tile entities in the chunk
        """
        if (cx, cz) in self.blocks_cache:
            return self.blocks_cache[(cx, cz)]

        chunk = Chunk(cx, cz, self._wrapper.get_blocks)
        self.blocks_cache[(cx, cz)] = chunk
        return self.blocks_cache[(cx, cz)]

    def get_block(self, x: int, y: int, z: int) -> str:
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
        chunk = self.get_chunk(cx, cz)
        block = chunk[offset_x, y, offset_z].blocks
        return self._wrapper.mapping_handler[block]

    def get_sub_chunks(
        self, *args: Union[slice, int]
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
                blocks_slice_to_chunk_slice(s_x) if chunk_pos
                == first_chunk else slice(None)
            )
            z_slice_for_chunk = (
                blocks_slice_to_chunk_slice(s_z) if chunk_pos
                == last_chunk else slice(None)
            )
            chunk = self.get_chunk(*chunk_pos)
            yield chunk[x_slice_for_chunk, s_y, z_slice_for_chunk]

    def run_operation_from_operation_name(
        self, operation_name: str, *args
    ) -> Optional[Exception]:
        operation_module = import_module(f"operations.{operation_name}")
        operation_class_name = "".join(x.title() for x in operation_name.split("_"))
        operation_class = getattr(operation_module, operation_class_name)
        operation_instance = operation_class(*args)
        try:
            self.run_operation(operation_instance)
        except Exception as e:
            self._revert_all_chunks()
            return e

        self.history_manager.add_operation(operation_instance)
        self._save_to_undo()

    def _revert_all_chunks(self):
        for chunk_pos, chunk in self.blocks_cache.items():
            if chunk.previous_unsaved_state is None:
                continue

            self.blocks_cache[chunk_pos] = chunk.previous_unsaved_state

    def _save_to_undo(self):
        for chunk in self.blocks_cache.values():
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
        path = os.path.join(
            get_temp_dir(self._directory),
            f"Operation_{self.history_manager.undo_stack.size()}",
        )
        for chunk_name in os.listdir(path):
            if not chunk_name.startswith("chunk"):
                continue

            cx, cz = chunk_name.split("_")[1:]
            cx, cz = int(cx), int(cz)
            if (cx, cz) in self.blocks_cache:
                self.blocks_cache[(cx, cz)].load_from_file(path)

        self.history_manager.undo()

    def redo(self):
        operation_to_redo = self.history_manager.redo()
        self.run_operation(operation_to_redo)
        self._save_to_undo()

    def run_operation(self, operation_instance: Operation) -> None:
        operation_instance.run_operation(self)

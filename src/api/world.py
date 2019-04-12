from __future__ import annotations

import itertools
import os
import shutil
from typing import Union, Generator, Dict, Optional, Callable
from importlib import import_module

import numpy

from api.block import Block, BlockManager
from api.data_structures import EntityContainer, EntityContext
from api.errors import ChunkDoesntExistException
from api.history_manager import ChunkHistoryManager
from api.chunk import Chunk, SubChunk
from api.operation import Operation
from api.paths import get_temp_dir
from utils.world_utils import (
    block_coords_to_chunk_coords,
    blocks_slice_to_chunk_slice,
    Coordinates,
)
from version_definitions import DefinitionManager


class WorldFormat:
    """
    Base class for World objects
    """

    block_manager: BlockManager = None
    _materials = None

    def __init__(
        self,
        directory: str,
        definitions: str,
        get_blockstate_adapter: Optional[Callable[[str], Block]] = None,
    ):
        self._directory = directory
        self._materials = DefinitionManager(definitions)
        self.block_manager = BlockManager()

        if get_blockstate_adapter:
            self.get_blockstate: Callable[[str], Block] = get_blockstate_adapter

    @classmethod
    def load(
        cls,
        directory: str,
        definitions,
        get_blockstate_adapter: Optional[Callable[[str], Block]] = None,
    ) -> World:
        """
        Loads the Minecraft world contained in the given directory with the supplied definitions

        :param directory: The directory of the world to load
        :param definitions: The definitions to load the world with
        :param get_blockstate_adapter: Adapter function used to convert version specific blockstate data
        :return: The loaded world in a `World` object
        """
        raise NotImplementedError()

    def get_entities(self, cx: int, cz: int) -> dict:
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

    def get_blockstate(self, blockstate: str) -> Block:
        """
        Converts a version-specific blockstate string into a :class:`api.blocks.Block` object by parsing the blockstate
        and handling any addition logic that needs to be done (IE: Adding an extra block when `waterlogged=true` for
        Java edition). This method is replaced at runtime with the version specific handler.

        :param blockstate: The blockstate string to parse/convert
        :return: The resulting Block object
        """

        namespace, base_name, properties = Block.parse_blockstate_string(blockstate)
        return Block(namespace=namespace, base_name=base_name, properties=properties)


class World:
    """
    Class that handles world editing of any world format via an separate and flexible data format
    """

    def __init__(self, directory: str, root_tag, wrapper: WorldFormat):
        self._directory = directory
        shutil.rmtree(get_temp_dir(self._directory), ignore_errors=True)
        self._root_tag = root_tag
        self._wrapper = wrapper
        self.chunk_cache: Dict[Coordinates, Chunk] = {}
        self.history_manager = ChunkHistoryManager(get_temp_dir(self._directory))
        self._deleted_chunks = set()

    def exit(self):
        # TODO: add "unsaved changes" check before exit
        shutil.rmtree(get_temp_dir(self._directory), ignore_errors=True)

    @property
    def block_manager(self) -> BlockManager:
        """
        Allows access to the :class:`api.blocks.BlockManager` instance for this World
        :return: The instance of the :class:`api.blocks.BlockManager`
        """
        return self._wrapper.block_manager

    def get_block_instance(self, blockstate: str) -> Block:
        """
        Converts the (possibly) version specific blockstate string into a :class:`api.blocks.Block`

        :param blockstate: The blockstate string to convert
        :return: The resulting :class:`api.blocks.Block` object
        """
        return self._wrapper.get_blockstate(blockstate)

    def get_chunk(self, cx: int, cz: int) -> Chunk:
        """
        Gets the chunk data of the specified chunk coordinates

        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :return: The blocks, entities, and tile entities in the chunk
        """
        if (cx, cz) in self.chunk_cache:
            return self.chunk_cache[(cx, cz)]

        chunk = Chunk(
            cx,
            cz,
            blocks=self._wrapper.get_blocks(cx, cz),
            entities=self._wrapper.get_entities(cx, cz),
        )
        self.chunk_cache[(cx, cz)] = chunk
        self.history_manager.add_original_chunk(chunk)
        return self.chunk_cache[(cx, cz)]

    def get_entities(self, cx: int, cz: int):
        return self._wrapper.get_entities(cx, cz)

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
            raise ChunkDoesntExistException(f"Chunk ({cx},{cz}) has been deleted")

        chunk = self.get_chunk(cx, cz)
        block = chunk[offset_x, y, offset_z].blocks
        return self._wrapper.block_manager[block]

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
    ):  # Currently O(n^3), maybe get down to O(n)?
        def get_coords(ent):
            return tuple(ent["Pos"])

        chunk_map = {}
        chunk_entities_map = {}
        immutable_entities_map = {}
        for subbox in box.subboxes():
            slice = subbox.to_slice()
            for subchunk in self.get_sub_chunks(*slice):
                chunk_coords = (subchunk._parent.cx, subchunk._parent.cz)
                cx, cz = chunk_coords
                entities = self.get_entities(cx, cz)

                entities_in_box = list(
                    filter(lambda e: get_coords(e) in subbox, entities)
                )
                entities_not_in_box = tuple(
                    filter(lambda e: get_coords(e) not in subbox, entities)
                )

                chunk_entities_map[chunk_coords] = entities_in_box
                immutable_entities_map[chunk_coords] = entities_not_in_box

                """
                chunk_entities_map[chunk_coords] = ent_list = [
                    ent for ent in entities if get_coords(ent) in subbox
                ]
                if len(ent_list) == 0:
                    del chunk_entities_map[chunk_coords]
                """

                if chunk_coords not in chunk_map:
                    chunk_map[chunk_coords] = subchunk._parent

        #        print(chunk_map)
        return EntityContext(
            EntityContainer(chunk_entities_map), immutable_entities_map, chunk_map
        )

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

import itertools
from typing import Tuple, Union, Generator, Dict
from importlib import import_module

import numpy

from api.history import HistoryManager
from api.selection import Selection
from utils.world_utils import block_coords_to_chunk_coords, blocks_slice_to_chunk_slice, Coordinates


class WorldFormat:
    """
    Base class for World objects
    """
    mapping_handler: numpy.ndarray = None

    @classmethod
    def load(cls, directory: str) -> "World":
        raise NotImplementedError()

    def get_chunk(self, cx: int, cz: int) -> Tuple[numpy.ndarray, dict, dict]:
        raise NotImplementedError()

    @classmethod
    def from_unified_format(cls, unified: "World") -> "WorldFormat":
        """
        Converts the passed object to the specific implementation

        :param unified: The object to convert
        :return object: The result of the conversion, None if not successful
        """
        raise NotImplementedError()

    def to_unified_format(self) -> "World":
        """
        Converts the current object to the Unified format
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
        self._root_tag = root_tag
        self._wrapper = wrapper
        self.blocks_cache: Dict[Coordinates, Selection] = {}
        self.history_manager = HistoryManager()

    @property
    def block_definitions(self):
        return self._wrapper.mapping_handler

    def get_chunk(self, cx: int, cz: int) -> Tuple[Selection, dict, dict]:
        """
        Gets the chunk data of the specified chunk coordinates

        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :return: The blocks, entities, and tile entities in the chunk
        """
        if (cx, cz) in self.blocks_cache:
            return self.blocks_cache[(cx, cz)], {}, {}
        chunk = self._wrapper.get_chunk(cx, cz)
        self.blocks_cache[(cx, cz)] = Selection(chunk[0])
        return self.blocks_cache[(cx, cz)], chunk[1], chunk[2]

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
        blocks, entities, tile_entities = self.get_chunk(cx, cz)

        if (x,y,z) in self.history_manager:
            print(f"Block at {(x,y,z)} has been changed")

        return self._wrapper.mapping_handler[blocks[offset_x, y, offset_z].blocks]

    def get_blocks(self, *args: Union[slice, int]) -> Generator[Selection, None, None]:
        length = len(args)
        if length == 3:
            s_x, s_y, s_z = args
        elif length == 6:
            s_x, s_y, s_z = slice(args[0], args[3]), slice(args[1], args[4]), slice(args[2], args[5])
        elif length == 9:
            s_x, s_y, s_z = slice(args[0], args[3], args[6]), slice(args[1], args[4], args[7]),\
                            slice(args[2], args[5], args[8])
        else:
            raise IndexError("Length of parameters to 'get_blocks' should be 3, 6 or 9")

        if not (
            isinstance(s_x, slice)
            and isinstance(s_y, slice)
            and isinstance(s_z, slice)
        ):
            raise IndexError()

        return self.get_blocks_slice(s_x, s_y, s_z)

    def get_blocks_slice(
        self, x_slice: slice, y_slice: slice, z_slice: slice
    ) -> Generator[Selection, None, None]:
        first_chunk = block_coords_to_chunk_coords(x_slice.start, z_slice.start)
        last_chunk = block_coords_to_chunk_coords(x_slice.stop, x_slice.stop)
        for chunk in itertools.product(
                range(first_chunk[0], last_chunk[0] + 1),
                range(first_chunk[1], last_chunk[1] + 1)
        ):
            x_slice_for_chunk = blocks_slice_to_chunk_slice(x_slice) if chunk == first_chunk else slice(None)
            z_slice_for_chunk = blocks_slice_to_chunk_slice(z_slice) if chunk == last_chunk else slice(None)
            blocks = self.get_chunk(*chunk)[0]
            yield blocks[x_slice_for_chunk, y_slice, z_slice_for_chunk]

    def get_blocks_bounded(self, *args: int) -> Generator[Selection, None, None]:
        return self.get_blocks_slice(slice(args[0], args[1]), slice(args[2], args[3]), slice(args[4], args[5]))

    def get_blocks_stepped(self, *args: int) -> Generator[Selection, None, None]:
        return self.get_blocks_slice(
            slice(args[0], args[1], args[6]), slice(args[2], args[3], args[7]), slice(args[4], args[5], args[8])
        )

    def run_operation(self, operation_name: str, *args) -> None:
        operation_module = import_module(f"operations.{operation_name}")
        operation_class_name = "".join(x.title() for x in operation_name.split("_"))
        operation_class = getattr(operation_module, operation_class_name)
        operation_instance = operation_class(*args)
        operation_instance.run_operation(self)

        self.history_manager.add_operation(operation_instance)

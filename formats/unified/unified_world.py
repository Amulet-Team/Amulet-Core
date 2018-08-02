from typing import Union, Sequence, Tuple
import functools

import numpy

import world_utils
from api.world import WorldFormat


def method_not_implemented(*args, **kwargs):
    raise NotImplementedError()


class UnifiedWorld:

    def __init__(self, directory: str, root_tag, wrapper: WorldFormat):
        self._directory = directory
        self._root_tag = root_tag
        self._wrapper = wrapper
        self.mapping_handler = wrapper.mapping_handler

        self._load_space()

        self._blocks = numpy.zeros((256, 256, 256), dtype=numpy.uint16)

    @functools.lru_cache(maxsize=8)
    def get_chunk(self, cx: int, cz: int) -> Tuple[numpy.ndarray, dict, dict]:
        return self._wrapper.d_load_chunk(cx, cz)

    def d_load_chunk(self, cx: int, cz: int):
        return self._wrapper.d_load_chunk(cx, cz)

    def _load_space(self):
        # print(self._root_tag)
        self._wrapper.d_load_chunk(0, 0)

    def get_block(self, x: int, y: int, z: int) -> str:
        if not (0 <= y <= 255):
            raise IndexError("The supplied Y coordinate must be between 0 and 255")

        cx, cz = world_utils.block_coords_to_chunk_coords(x, z)
        offset_x, offset_z = x - 16 * cx, z - 16 * cz
        blocks, entities, tile_entities = self.get_chunk(cx, cz)

        return self.mapping_handler[blocks[offset_x, y, offset_z].item()]

    # return self._blocks[x, y, z]

    def get_blocks(self, *args: Union[Sequence[slice], Sequence[int]]) -> numpy.ndarray:
        length = len(args)
        if 3 <= length < 6:
            s_x, s_y, s_z = args[0:3]
            if not (
                isinstance(s_x, slice)
                and isinstance(s_y, slice)
                and isinstance(s_z, slice)
            ):
                raise IndexError()

            return self.get_blocks_slice(s_x, s_y, s_z)

    def get_blocks_slice(
        self, x_slice: slice, y_slice: slice, z_slice: slice
    ) -> numpy.ndarray:
        return self._blocks[x_slice, y_slice, z_slice]

    def get_blocks_bounded(self, *args: Sequence[int]) -> numpy.ndarray:
        return self._blocks[args[0]:args[1], args[2]:args[3], args[4]:args[5]]

    def get_blocks_stepped(self, *args: Sequence[int]) -> numpy.ndarray:
        return self._blocks[
            args[0]:args[1]:args[6], args[2]:args[3]:args[7], args[4]:args[5]:args[8]
        ]

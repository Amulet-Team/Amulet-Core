from typing import List

import numpy as np
from utils.world_utils import Coordinates


class CachedChunks:
    def __init__(self, chunks_to_cache: np.ndarray, least_chunk_position: Coordinates) -> None:
        self.chunks_to_cache = chunks_to_cache
        self.least_chunk_position = least_chunk_position

    def __contains__(self, item):
        if self.chunks_to_cache is None or self.least_chunk_position is None:
            return False
        if isinstance(item, (tuple, list)):
            if len(item) != 2:
                raise Exception(f"Can't check if CachedChunks contains a list of {len(item)} elements {type(item)}")
            least_blocks = self.least_chunk_position[0], self.least_chunk_position[1]
            most_blocks = least_blocks[0] + (self.chunks_to_cache.shape[0] // 16),\
                          least_blocks[1] + (self.chunks_to_cache.shape[2] // 16)
            if most_blocks[0] >= item[0] >= least_blocks[0] and most_blocks[1] >= item[1] >= least_blocks[1]:
                return True
            return False
        raise Exception(f"Don't know how to find item from type {type(item)} in CachedChunks")

    def __getitem__(self, item):
        if item not in self:
            raise Exception(f"The chunk {item} does not exist in CachedChunks")
        chunk_relative_pos = item[0] - self.least_chunk_position[0], item[1] - self.least_chunk_position[1]
        return self.chunks_to_cache[chunk_relative_pos[0]:chunk_relative_pos[0]+16, :,
                                    chunk_relative_pos[1]:chunk_relative_pos[1]+16]


class ListCachedChunks:
    def __init__(self):
        self.list_of_cached_chunks: List[CachedChunks] = []

    def add_cached_chunks(self, cached_chunks: np.ndarray, least_chunk_position: Coordinates):
        self.list_of_cached_chunks.append(CachedChunks(cached_chunks, least_chunk_position))

    def __contains__(self, item):
        for cached_chunks in self.list_of_cached_chunks:
            if item in cached_chunks:
                return True
        return False

    def __getitem__(self, item):
        for cached_chunks in self.list_of_cached_chunks:
            if item in cached_chunks:
                return cached_chunks[item]
        return None

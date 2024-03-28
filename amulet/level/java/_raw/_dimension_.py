from typing import Iterable

from amulet.api.data_types import ChunkCoordinates
from amulet.biome import Biome
from amulet.block import BlockStack, Block
from amulet.data_types import DimensionId
from amulet.level.abc import RawDimension
from amulet.selection import SelectionGroup
from ..chunk import JavaChunk
from ._chunk import JavaRawChunk
from ._typing import InternalDimensionId
from ...abc._raw_level import ChunkT, RawChunkT


class JavaRawDimension(

    RawDimension[JavaRawChunk, JavaChunk]
):
    def __init__(
        self,
        dimension_path: InternalDimensionId,
        dimension_id: DimensionId,
        bounds: SelectionGroup,
    ) -> None:
        self._dimension_path = dimension_path
        self._dimension_id = dimension_id
        self._bounds = bounds

    @property
    def dimension_id(self) -> DimensionId:
        return self._dimension_id

    def bounds(self) -> SelectionGroup:
        return self._bounds

    def default_block(self) -> BlockStack:
        return BlockStack(Block(self._r.platform, self._r.version, "minecraft", "air"))

    def default_biome(self) -> Biome:
        pass

    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        pass

    def has_chunk(self, cx: int, cz: int) -> bool:
        pass

    def delete_chunk(self, cx: int, cz: int) -> None:
        pass

    def get_raw_chunk(self, cx: int, cz: int) -> RawChunkT:
        pass

    def set_raw_chunk(self, cx: int, cz: int, chunk: RawChunkT) -> None:
        pass

    def raw_chunk_to_native_chunk(self, cx: int, cz: int, raw_chunk: RawChunkT) -> ChunkT:
        pass

    def native_chunk_to_raw_chunk(self, cx: int, cz: int, chunk: ChunkT) -> RawChunkT:
        pass

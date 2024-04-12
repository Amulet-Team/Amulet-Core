from __future__ import annotations
from typing import Iterable, TYPE_CHECKING, Callable

from amulet.api.data_types import ChunkCoordinates
from amulet.biome import Biome
from amulet.block import BlockStack
from amulet.data_types import DimensionId
from amulet.level.abc import RawDimension, RawLevelFriend
from amulet.selection import SelectionGroup

from amulet.level.java.anvil import ChunkDataType, AnvilDimension
from amulet.level.java.chunk import JavaChunk
from ._typing import InternalDimensionId


if TYPE_CHECKING:
    from ._level import JavaRawLevel


class JavaRawDimension(
    RawLevelFriend["JavaRawLevel"],
    RawDimension[ChunkDataType, JavaChunk]
):
    def __init__(
        self,
        raw_level_ref: Callable[[], JavaRawLevel | None],
        anvil_dimension: AnvilDimension,
        relative_path: InternalDimensionId,
        dimension_id: DimensionId,
        bounds: SelectionGroup,
        default_block: BlockStack,
        default_biome: Biome,
    ) -> None:
        super().__init__(raw_level_ref)
        self._anvil_dimension = anvil_dimension
        self._relative_path = relative_path
        self._dimension_id = dimension_id
        self._bounds = bounds
        self._default_block = default_block
        self._default_biome = default_biome

    @property
    def dimension_id(self) -> DimensionId:
        return self._dimension_id

    @property
    def relative_path(self) -> InternalDimensionId:
        return self._relative_path

    def bounds(self) -> SelectionGroup:
        return self._bounds

    def default_block(self) -> BlockStack:
        return self._default_block

    def default_biome(self) -> Biome:
        return self._default_biome

    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        yield from self._anvil_dimension.all_chunk_coords()

    def has_chunk(self, cx: int, cz: int) -> bool:
        return self._anvil_dimension.has_chunk(cx, cz)

    def delete_chunk(self, cx: int, cz: int) -> None:
        self._anvil_dimension.delete_chunk(cx, cz)

    def get_raw_chunk(self, cx: int, cz: int) -> ChunkDataType:
        return self._anvil_dimension.get_chunk_data(cx, cz)

    def set_raw_chunk(self, cx: int, cz: int, chunk: ChunkDataType) -> None:
        self._anvil_dimension.put_chunk_data(cx, cz, chunk)

    def raw_chunk_to_native_chunk(self, cx: int, cz: int, raw_chunk: ChunkDataType) -> JavaChunk:
        raise NotImplementedError

    def native_chunk_to_raw_chunk(self, cx: int, cz: int, chunk: JavaChunk) -> ChunkDataType:
        raise NotImplementedError

    def compact(self) -> None:
        """Compact all region files"""
        self._anvil_dimension.compact()
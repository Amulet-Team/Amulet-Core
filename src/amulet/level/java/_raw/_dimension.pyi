from typing import Callable, Iterable

from amulet.biome import Biome as Biome
from amulet.block import BlockStack as BlockStack
from amulet.data_types import ChunkCoordinates as ChunkCoordinates
from amulet.data_types import DimensionId as DimensionId
from amulet.level.abc import RawDimension as RawDimension
from amulet.level.abc import RawLevelFriend as RawLevelFriend
from amulet.level.java.anvil import AnvilDimension as AnvilDimension
from amulet.level.java.anvil import RawChunkType as RawChunkType
from amulet.level.java.chunk import JavaChunk as JavaChunk
from amulet.selection import SelectionGroup as SelectionGroup

from ._chunk import decode_chunk as decode_chunk
from ._chunk import encode_chunk as encode_chunk
from ._level import JavaRawLevel as JavaRawLevel
from ._typing import InternalDimensionId as InternalDimensionId

class JavaRawDimension(
    RawLevelFriend["JavaRawLevel"], RawDimension[RawChunkType, JavaChunk]
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
    ) -> None: ...
    @property
    def dimension_id(self) -> DimensionId: ...
    @property
    def relative_path(self) -> InternalDimensionId: ...
    def bounds(self) -> SelectionGroup: ...
    def default_block(self) -> BlockStack: ...
    def default_biome(self) -> Biome: ...
    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]: ...
    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def delete_chunk(self, cx: int, cz: int) -> None: ...
    def get_raw_chunk(self, cx: int, cz: int) -> RawChunkType: ...
    def set_raw_chunk(self, cx: int, cz: int, chunk: RawChunkType) -> None: ...
    def raw_chunk_to_native_chunk(
        self, raw_chunk: RawChunkType, cx: int, cz: int
    ) -> JavaChunk: ...
    def native_chunk_to_raw_chunk(
        self, chunk: JavaChunk, cx: int, cz: int
    ) -> RawChunkType: ...
    def compact(self) -> None:
        """Compact all region files"""

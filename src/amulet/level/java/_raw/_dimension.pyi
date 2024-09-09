from __future__ import annotations

import types
import typing
from builtins import str as DimensionId
from builtins import str as InternalDimensionId

import amulet.level.abc._raw_level
from amulet.biome import Biome
from amulet.block import BlockStack
from amulet.level.abc._raw_level import RawDimension, RawLevelFriend
from amulet.level.java._raw._chunk import decode_chunk, encode_chunk
from amulet.level.java.anvil._dimension import AnvilDimension
from amulet.level.java.chunk import JavaChunk
from amulet.selection.group import SelectionGroup

__all__ = [
    "AnvilDimension",
    "Biome",
    "BlockStack",
    "ChunkCoordinates",
    "DimensionId",
    "InternalDimensionId",
    "JavaChunk",
    "JavaRawDimension",
    "RawChunkType",
    "RawDimension",
    "RawLevelFriend",
    "SelectionGroup",
    "decode_chunk",
    "encode_chunk",
]

class JavaRawDimension(
    amulet.level.abc._raw_level.RawLevelFriend, amulet.level.abc._raw_level.RawDimension
):
    def __init__(
        self,
        raw_level_ref: typing.Callable[[], JavaRawLevel | None],
        anvil_dimension: AnvilDimension,
        relative_path: InternalDimensionId,
        dimension_id: DimensionId,
        bounds: SelectionGroup,
        default_block: BlockStack,
        default_biome: Biome,
    ) -> None: ...
    def all_chunk_coords(self) -> typing.Iterable[ChunkCoordinates]: ...
    def bounds(self) -> SelectionGroup: ...
    def compact(self) -> None:
        """
        Compact all region files
        """

    def default_biome(self) -> Biome: ...
    def default_block(self) -> BlockStack: ...
    def delete_chunk(self, cx: int, cz: int) -> None: ...
    def get_raw_chunk(self, cx: int, cz: int) -> RawChunkType: ...
    def has_chunk(self, cx: int, cz: int) -> bool: ...
    def native_chunk_to_raw_chunk(
        self, chunk: JavaChunk, cx: int, cz: int
    ) -> RawChunkType: ...
    def raw_chunk_to_native_chunk(
        self, raw_chunk: RawChunkType, cx: int, cz: int
    ) -> JavaChunk: ...
    def set_raw_chunk(self, cx: int, cz: int, chunk: RawChunkType) -> None: ...
    @property
    def dimension_id(self) -> DimensionId: ...
    @property
    def relative_path(self) -> InternalDimensionId: ...

ChunkCoordinates: types.GenericAlias  # value = tuple[int, int]
RawChunkType: types.GenericAlias  # value = dict[str, amulet_nbt.NamedTag]

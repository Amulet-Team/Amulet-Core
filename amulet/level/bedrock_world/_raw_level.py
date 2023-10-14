from typing import Iterable

from amulet.api.chunk import Chunk
from amulet.api.data_types import DimensionID, ChunkCoordinates
from amulet.level.base_level import RawLevel
from amulet.level.base_level._raw_level import PlayerIDT, RawPlayerT, NativeChunkT, RawChunkT


class BedrockRawLevel(RawLevel):
    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        raise NotImplementedError

    def has_chunk(self, dimension: DimensionID, cx: int, cz: int) -> bool:
        raise NotImplementedError

    def delete_chunk(self, dimension: DimensionID, cx: int, cz: int):
        raise NotImplementedError

    def get_raw_chunk(self, dimension: DimensionID, cx: int, cz: int) -> RawChunkT:
        raise NotImplementedError

    def set_raw_chunk(self, dimension: DimensionID, cx: int, cz: int, chunk: RawChunkT):
        raise NotImplementedError

    def get_native_chunk(self, dimension: DimensionID, cx: int, cz: int) -> NativeChunkT:
        raise NotImplementedError

    def set_native_chunk(self, dimension: DimensionID, cx: int, cz: int, chunk: NativeChunkT):
        raise NotImplementedError

    def get_universal_chunk(self, dimension: DimensionID, cx: int, cz: int) -> Chunk:
        raise NotImplementedError

    def set_universal_chunk(self, dimension: DimensionID, cx: int, cz: int, chunk: Chunk):
        raise NotImplementedError

    def raw_to_native_chunk(self, chunk: RawChunkT) -> NativeChunkT:
        raise NotImplementedError

    def native_to_raw_chunk(self, chunk: NativeChunkT) -> RawChunkT:
        raise NotImplementedError

    def native_to_universal_chunk(self, chunk: NativeChunkT) -> Chunk:
        raise NotImplementedError

    def universal_to_native_chunk(self, chunk: Chunk) -> NativeChunkT:
        raise NotImplementedError

    def all_player_ids(self) -> Iterable[PlayerIDT]:
        raise NotImplementedError

    def has_player(self, player_id: PlayerIDT) -> bool:
        raise NotImplementedError

    def get_raw_player(self, player_id: PlayerIDT) -> RawPlayerT:
        raise NotImplementedError

    def set_raw_player(self, player_id: PlayerIDT, player: RawPlayerT):
        raise NotImplementedError

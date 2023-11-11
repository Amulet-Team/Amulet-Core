import numpy
from .anvil_2709 import Anvil2709Interface as ParentInterface
from .base_anvil_interface import ChunkDataType as ChunkDataType, ChunkPathType as ChunkPathType
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.api.data_types import AnyNDArray as AnyNDArray, BiomeType as BiomeType
from amulet.palette import BiomePalette as BiomePalette
from amulet.utils.world_utils import decode_long_array as decode_long_array, encode_long_array as encode_long_array
from amulet_nbt import CompoundTag, ListTag
from typing import Dict, Iterable, Optional, Tuple

class Anvil2844Interface(ParentInterface):
    """
    Note that some of these changes happened in earlier snapshots
    Chunk restructuring
    Contents of Level tag moved into root
    Some tags renamed from PascalCase to snake_case
        2844
        Level.Entities -> entities.
        Level.TileEntities -> block_entities.
        Level.TileTicks and Level.ToBeTicked have moved to block_ticks.
        Level.LiquidTicks and Level.LiquidsToBeTicked have moved to fluid_ticks.
        Level.Sections -> sections.
        Level.Structures -> structures.
        Level.Structures.Starts -> structures.starts.
        Level.Sections[].block_states -> sections[].block_states.
        Level.Sections[].biomes -> sections[].biomes
        Added yPos the minimum section y position in the chunk.
        Added below_zero_retrogen containing data to support below zero generation.
        Added blending_data containing data to support blending new world generation with existing chunks.
        2836
        Level.Sections[].BlockStates & Level.Sections[].Palette -> Level.Sections[].block_states.
        Level.Biomes -> Level.Sections[].biomes.
        Level.CarvingMasks[] is now long[] instead of byte[].
    """
    OldLevel: ChunkPathType
    Level: ChunkPathType
    Sections: ChunkPathType
    Entities: ChunkPathType
    BlockEntities: ChunkPathType
    BlockTicks: ChunkPathType
    ToBeTicked: Incomplete
    LiquidTicks: ChunkPathType
    LiquidsToBeTicked: Incomplete
    Structures: ChunkPathType
    yPos: ChunkPathType
    Biomes: Incomplete
    xPos: ChunkPathType
    zPos: ChunkPathType
    LastUpdate: ChunkPathType
    InhabitedTime: ChunkPathType
    Status: ChunkPathType
    PostProcessing: ChunkPathType
    Heightmaps: ChunkPathType
    def __init__(self) -> None: ...
    @staticmethod
    def minor_is_valid(key: int): ...
    def _get_floor_cy(self, data: ChunkDataType): ...
    def _decode_block_section(self, section: CompoundTag) -> Optional[Tuple[numpy.ndarray, list]]: ...
    @staticmethod
    def _decode_biome_palette(palette: ListTag) -> list[BiomeType]: ...
    def _decode_biome_section(self, section: CompoundTag) -> Optional[Tuple[numpy.ndarray, list]]: ...
    def _decode_biomes(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _decode_block_ticks(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _decode_fluid_ticks(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _encode_coords(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _encode_block_section(self, chunk: Chunk, sections: Dict[int, CompoundTag], palette: AnyNDArray, cy: int): ...
    @staticmethod
    def _encode_biome_palette(palette: Iterable[BiomeType]) -> ListTag: ...
    def _encode_biome_section(self, chunk: Chunk, sections: Dict[int, CompoundTag], cy: int): ...
    def _encode_biomes(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _encode_block_ticks(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _encode_fluid_ticks(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
    def _post_encode_remove_old_level(self, chunk: Chunk, data: ChunkDataType, floor_cy: int, height_cy: int): ...
export = Anvil2844Interface

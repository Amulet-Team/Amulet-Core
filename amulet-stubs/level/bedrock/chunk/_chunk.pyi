from .components.chunk_version import ChunkVersionComponent as ChunkVersionComponent
from .components.finalised_state import FinalisedStateComponent as FinalisedStateComponent
from amulet.chunk import Chunk as Chunk
from amulet.chunk.components.biome import Biome2DComponent as Biome2DComponent, Biome3DComponent as Biome3DComponent
from amulet.chunk.components.block import BlockComponent as BlockComponent
from amulet.chunk.components.block_entity import BlockEntityComponent as BlockEntityComponent
from amulet.chunk.components.entity import EntityComponent as EntityComponent
from amulet.chunk.components.height_2d import Height2DComponent as Height2DComponent
from amulet.version import SemanticVersion as SemanticVersion, VersionRange as VersionRange

class BedrockChunk(Chunk): ...

class BedrockChunk0(BedrockChunk, ChunkVersionComponent, BlockComponent, BlockEntityComponent, Biome2DComponent, EntityComponent, FinalisedStateComponent, Height2DComponent):
    def __init__(self, max_version: SemanticVersion) -> None: ...

class BedrockChunk29(BedrockChunk, ChunkVersionComponent, BlockComponent, BlockEntityComponent, Biome3DComponent, EntityComponent, FinalisedStateComponent, Height2DComponent):
    def __init__(self, max_version: SemanticVersion) -> None: ...

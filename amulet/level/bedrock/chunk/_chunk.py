from __future__ import annotations
from amulet.chunk import Chunk
from amulet.version import VersionRange, VersionNumber

from amulet.chunk.components.biome import Biome2DComponent
from amulet.chunk.components.biome import Biome3DComponent
from amulet.chunk.components.block import BlockComponent
from amulet.chunk.components.block_entity import BlockEntityComponent
from amulet.chunk.components.entity import EntityComponent
from amulet.chunk.components.height_2d import Height2DComponent

from .components.finalised_state import FinalisedStateComponent
from .components.chunk_version import ChunkVersionComponent
from .components.raw_chunk import RawChunkComponent


class BedrockChunk(Chunk):
    pass


class BedrockChunk0(
    BedrockChunk,
    RawChunkComponent,
    ChunkVersionComponent,
    BlockComponent,
    BlockEntityComponent,
    Biome2DComponent,
    EntityComponent,
    FinalisedStateComponent,
    Height2DComponent,
):
    def __init__(self, max_version: VersionNumber) -> None:
        version_range = VersionRange(
            "bedrock",
            VersionNumber(1, 0, 0),
            max_version,
        )
        RawChunkComponent.__init__(self)
        ChunkVersionComponent.__init__(self, 0, 28, 0)
        BlockComponent.__init__(self, version_range, (16, 16, 16), 0)
        BlockEntityComponent.__init__(self, version_range)
        Biome2DComponent.__init__(self, version_range, (16, 16), 0)
        EntityComponent.__init__(self, version_range)
        FinalisedStateComponent.__init__(self)
        Height2DComponent.__init__(self)


class BedrockChunk29(
    BedrockChunk,
    RawChunkComponent,
    ChunkVersionComponent,
    BlockComponent,
    BlockEntityComponent,
    Biome3DComponent,
    EntityComponent,
    FinalisedStateComponent,
    Height2DComponent,
):
    def __init__(self, max_version: VersionNumber) -> None:
        version_range = VersionRange(
            "bedrock",
            VersionNumber(1, 0, 0),
            max_version,
        )
        RawChunkComponent.__init__(self)
        ChunkVersionComponent.__init__(self, 29, 99999, 29)
        BlockComponent.__init__(self, version_range, (16, 16, 16), 0)
        BlockEntityComponent.__init__(self, version_range)
        Biome3DComponent.__init__(self, version_range, (16, 16, 16), 0)
        EntityComponent.__init__(self, version_range)
        FinalisedStateComponent.__init__(self)
        Height2DComponent.__init__(self)

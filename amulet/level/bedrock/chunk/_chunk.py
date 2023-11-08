from __future__ import annotations
from abc import ABC
from amulet.chunk import Chunk
from amulet.version import VersionRange, SemanticVersion

from amulet.chunk.components.biome import Biome2DComponent
from amulet.chunk.components.biome import Biome3DComponent
from amulet.chunk.components.block import BlockComponent
from amulet.chunk.components.block_entity import BlockEntityComponent
from amulet.chunk.components.entity import EntityComponent
from amulet.chunk.components.height_2d import Height2DComponent

from .components.finalised_state import FinalisedStateComponent
from .components.chunk_version import ChunkVersionComponent


class BedrockChunk(Chunk):
    pass


class BedrockChunk0(
    BedrockChunk,
    ChunkVersionComponent,
    BlockComponent,
    BlockEntityComponent,
    Biome2DComponent,
    EntityComponent,
    FinalisedStateComponent,
    Height2DComponent,
):
    def __init__(self, max_version: SemanticVersion):
        version_range = VersionRange(
            SemanticVersion("bedrock", (1, 0, 0)),
            max_version,
        )
        ChunkVersionComponent.__init__(self, 0, 28, 0)
        BlockComponent.__init__(self, version_range, (16, 16, 16), 0)
        BlockEntityComponent.__init__(self, version_range)
        Biome2DComponent.__init__(self, version_range, (16, 16), 0)
        EntityComponent.__init__(self, version_range)
        FinalisedStateComponent.__init__(self)
        Height2DComponent.__init__(self)


class BedrockChunk29(
    BedrockChunk,
    ChunkVersionComponent,
    BlockComponent,
    BlockEntityComponent,
    Biome3DComponent,
    EntityComponent,
    FinalisedStateComponent,
    Height2DComponent,
):
    def __init__(self, max_version: SemanticVersion):
        version_range = VersionRange(
            SemanticVersion("bedrock", (1, 0, 0)),
            max_version,
        )
        ChunkVersionComponent.__init__(self, 29, 99999, 29)
        BlockComponent.__init__(self, version_range, (16, 16, 16), 0)
        BlockEntityComponent.__init__(self, version_range)
        Biome3DComponent.__init__(self, version_range, (16, 16, 16), 0)
        EntityComponent.__init__(self, version_range)
        FinalisedStateComponent.__init__(self)
        Height2DComponent.__init__(self)

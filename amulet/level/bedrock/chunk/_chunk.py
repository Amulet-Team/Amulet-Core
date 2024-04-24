from __future__ import annotations

from typing import TypeVar, Self, TypeAlias, cast
from types import UnionType

import numpy

from amulet.version import VersionNumber, VersionRange
from amulet.chunk import Chunk
from amulet.block import BlockStack
from amulet.biome import Biome

from amulet.chunk.components.biome import (
    Biome2DComponent,
    Biome2DComponentData,
    Biome3DComponent,
    Biome3DComponentData,
)
from amulet.chunk.components.block import BlockComponent, BlockComponentData
from amulet.chunk.components.block_entity import (
    BlockEntityComponent,
    BlockEntityComponentData,
)
from amulet.chunk.components.entity import EntityComponent, EntityComponentData
from amulet.chunk.components.height_2d import Height2DComponent

from .components.finalised_state import FinalisedStateComponent
from .components.chunk_version import ChunkVersionComponent
from .components.raw_chunk import RawChunkComponent

T = TypeVar("T")


class BedrockChunk0(Chunk):
    components = frozenset(
        (
            RawChunkComponent,
            ChunkVersionComponent,
            FinalisedStateComponent,
            BlockComponent,
            BlockEntityComponent,
            Biome2DComponent,
            EntityComponent,
            Height2DComponent,
        )
    )

    @classmethod
    def new(
        cls, max_version: VersionNumber, default_block: BlockStack, default_biome: Biome
    ) -> Self:
        version_range = VersionRange(
            "bedrock",
            VersionNumber(1, 0, 0),
            max_version,
        )

        return cls.from_component_data(
            {
                RawChunkComponent: None,
                ChunkVersionComponent: 0,
                FinalisedStateComponent: 2,
                BlockComponent: BlockComponentData(
                    version_range, (16, 16, 16), 0, default_block
                ),
                BlockEntityComponent: BlockEntityComponentData(version_range),
                EntityComponent: EntityComponentData(version_range),
                Biome2DComponent: Biome2DComponentData(
                    version_range, (16, 16), 0, default_biome
                ),
                Height2DComponent: numpy.zeros((16, 16), dtype=numpy.int64),
            }
        )  # type: ignore


class BedrockChunk29(Chunk):
    components = frozenset(
        (
            RawChunkComponent,
            ChunkVersionComponent,
            FinalisedStateComponent,
            BlockComponent,
            BlockEntityComponent,
            Biome3DComponent,
            EntityComponent,
            Height2DComponent,
        )
    )

    @classmethod
    def new(
        cls, max_version: VersionNumber, default_block: BlockStack, default_biome: Biome
    ) -> Self:
        version_range = VersionRange(
            "bedrock",
            VersionNumber(1, 0, 0),
            max_version,
        )

        return cls.from_component_data(
            {
                RawChunkComponent: None,
                ChunkVersionComponent: 29,
                FinalisedStateComponent: 2,
                BlockComponent: BlockComponentData(
                    version_range, (16, 16, 16), 0, default_block
                ),
                BlockEntityComponent: BlockEntityComponentData(version_range),
                EntityComponent: EntityComponentData(version_range),
                Biome3DComponent: Biome3DComponentData(
                    version_range, (16, 16, 16), 0, default_biome
                ),
                Height2DComponent: numpy.zeros((16, 16), dtype=numpy.int64),
            }
        )  # type: ignore


# TODO: Improve this if python/mypy#11673 gets fixed.
BedrockChunk: TypeAlias = cast(UnionType, BedrockChunk0 | BedrockChunk29)

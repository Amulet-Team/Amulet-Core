from __future__ import annotations

from typing import TypeVar, Self, TypeAlias, cast
from types import UnionType

import numpy

from amulet.version import VersionNumber, VersionRange
from amulet.chunk import Chunk, ComponentDataMapping
from amulet.block import BlockStack, Block
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


def _get_components(
    chunk_version: int,
    version_range: VersionRange,
    default_block: BlockStack,
    default_biome: Biome,
) -> ComponentDataMapping:
    components: ComponentDataMapping = {}  # type: ignore
    components[RawChunkComponent] = None
    components[ChunkVersionComponent] = chunk_version
    components[FinalisedStateComponent] = 2
    components[BlockComponent] = BlockComponentData(
        version_range, (16, 16, 16), default_block
    )
    components[BlockEntityComponent] = BlockEntityComponentData(version_range)
    components[EntityComponent] = EntityComponentData(version_range)
    if chunk_version >= 29:
        components[Biome3DComponent] = Biome3DComponentData(
            version_range, (16, 16, 16), default_biome
        )
    else:
        components[Biome2DComponent] = Biome2DComponentData(
            version_range, (16, 16), default_biome
        )
    components[Height2DComponent] = numpy.zeros((16, 16), dtype=numpy.int64)
    return components


class BedrockChunk0(Chunk):
    components = frozenset(
        _get_components(
            0,
            VersionRange(
                "bedrock",
                VersionNumber(1, 0, 0),
                VersionNumber(1, 0, 0),
            ),
            BlockStack(Block("bedrock", VersionNumber(1, 0, 0), "", "")),
            Biome("bedrock", VersionNumber(1, 0, 0), "", ""),
        )
    )

    @classmethod
    def new(
        cls, max_version: VersionNumber, default_block: BlockStack, default_biome: Biome
    ) -> Self:
        return cls.from_component_data(
            _get_components(
                0,
                VersionRange(
                    "bedrock",
                    VersionNumber(1, 0, 0),
                    max_version,
                ),
                default_block,
                default_biome,
            )
        )


class BedrockChunk29(Chunk):
    components = frozenset(
        _get_components(
            29,
            VersionRange(
                "bedrock",
                VersionNumber(1, 0, 0),
                VersionNumber(1, 0, 0),
            ),
            BlockStack(Block("bedrock", VersionNumber(1, 0, 0), "", "")),
            Biome("bedrock", VersionNumber(1, 0, 0), "", ""),
        )
    )

    @classmethod
    def new(
        cls, max_version: VersionNumber, default_block: BlockStack, default_biome: Biome
    ) -> Self:
        return cls.from_component_data(
            _get_components(
                29,
                VersionRange(
                    "bedrock",
                    VersionNumber(1, 0, 0),
                    max_version,
                ),
                default_block,
                default_biome,
            )
        )


# TODO: Improve this if python/mypy#11673 gets fixed.
BedrockChunk: TypeAlias = cast(UnionType, BedrockChunk0 | BedrockChunk29)

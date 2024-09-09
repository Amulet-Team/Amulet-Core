from __future__ import annotations

import amulet.biome
import amulet.block
import amulet.chunk
import amulet.chunk_components
import amulet.level.java.chunk_components

__all__ = [
    "JavaChunk",
    "JavaChunk0",
    "JavaChunk1444",
    "JavaChunk1466",
    "JavaChunk2203",
    "JavaChunkNA",
]

class JavaChunk(amulet.chunk.Chunk):
    pass

class JavaChunk0(
    JavaChunk,
    amulet.level.java.chunk_components.JavaRawChunkComponent,
    amulet.level.java.chunk_components.DataVersionComponent,
    amulet.chunk_components.BlockComponent,
):
    def __init__(
        self,
        data_version: int,
        default_block: amulet.block.BlockStack,
        default_biome: amulet.biome.Biome,
    ) -> None: ...

class JavaChunk1444(
    JavaChunk,
    amulet.level.java.chunk_components.JavaRawChunkComponent,
    amulet.level.java.chunk_components.DataVersionComponent,
    amulet.chunk_components.BlockComponent,
):
    def __init__(
        self,
        data_version: int,
        default_block: amulet.block.BlockStack,
        default_biome: amulet.biome.Biome,
    ) -> None: ...

class JavaChunk1466(
    JavaChunk,
    amulet.level.java.chunk_components.JavaRawChunkComponent,
    amulet.level.java.chunk_components.DataVersionComponent,
    amulet.chunk_components.BlockComponent,
):
    def __init__(
        self,
        data_version: int,
        default_block: amulet.block.BlockStack,
        default_biome: amulet.biome.Biome,
    ) -> None: ...

class JavaChunk2203(
    JavaChunk,
    amulet.level.java.chunk_components.JavaRawChunkComponent,
    amulet.level.java.chunk_components.DataVersionComponent,
    amulet.chunk_components.BlockComponent,
):
    def __init__(
        self,
        data_version: int,
        default_block: amulet.block.BlockStack,
        default_biome: amulet.biome.Biome,
    ) -> None: ...

class JavaChunkNA(
    JavaChunk,
    amulet.level.java.chunk_components.JavaRawChunkComponent,
    amulet.level.java.chunk_components.DataVersionComponent,
    amulet.chunk_components.BlockComponent,
):
    def __init__(
        self, default_block: amulet.block.BlockStack, default_biome: amulet.biome.Biome
    ) -> None: ...

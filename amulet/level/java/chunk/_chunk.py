from typing import Self, TypeAlias, cast
from types import UnionType

import numpy

from amulet.chunk import Chunk, ComponentDataMapping
from amulet.chunk.components.height_2d import Height2DComponent
from amulet.level.java.chunk.components.raw_chunk import RawChunkComponent
from amulet.level.java.chunk.components.data_version import DataVersionComponent
from amulet.level.java.chunk.components.legacy_version import LegacyVersionComponent
from amulet.level.java.chunk.components.status import StatusComponent
from amulet.level.java.chunk.components.light_populated import LightPopulatedComponent
from amulet.level.java.chunk.components.terrain_populated import TerrainPopulatedComponent
from amulet.level.java.chunk.components.named_height_2d import NamedHeight2DComponent, NamedHeight2DData
from amulet.level.java.chunk.components.last_update import LastUpdateComponent


def _get_components(data_version: int) -> ComponentDataMapping:
    components: ComponentDataMapping = {}  # type: ignore

    components[RawChunkComponent] = None
    components[DataVersionComponent] = data_version
    components[LastUpdateComponent] = 0

    if data_version == -1:
        components[LegacyVersionComponent] = 1
    if data_version >= 3454:
        components[StatusComponent] = "minecraft:full"
    elif data_version >= 1912:
        components[StatusComponent] = "full"
    elif data_version >= 1444:
        components[StatusComponent] = "postprocessed"
    else:
        components[TerrainPopulatedComponent] = True
        components[LightPopulatedComponent] = True

    if data_version >= 1908:
        components[NamedHeight2DComponent] = NamedHeight2DData(
            (16, 16),
            {key: numpy.zeros((16, 16), dtype=numpy.int64) for key in ("WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "WORLD_SURFACE")}
        )
    if data_version >= 1503:
        components[NamedHeight2DComponent] = NamedHeight2DData(
            (16, 16),
            {key: numpy.zeros((16, 16), dtype=numpy.int64) for key in ("WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "LIGHT_BLOCKING", "WORLD_SURFACE")}
        )
    if data_version >= 1484:
        components[NamedHeight2DComponent] = NamedHeight2DData(
            (16, 16),
            {key: numpy.zeros((16, 16), dtype=numpy.int64) for key in ("WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "LIGHT_BLOCKING")}
        )
    if data_version >= 1466:
        components[NamedHeight2DComponent] = NamedHeight2DData(
            (16, 16),
            {key: numpy.zeros((16, 16), dtype=numpy.int64) for key in ("LIQUID", "SOLID", "LIGHT", "RAIN")}
        )
    else:
        components[Height2DComponent] = numpy.zeros((16, 16), dtype=numpy.int64)

    return components


class JavaChunkNA(Chunk):
    components = frozenset(_get_components(-1))

    @classmethod
    def new(cls) -> Self:
        self = cls.from_component_data(_get_components(-1))
        return self


class JavaChunk0(Chunk):
    """Added DataVersion"""

    components = frozenset(_get_components(0))

    @classmethod
    def new(cls, data_version: int) -> Self:
        if not 0 <= data_version < 1444:
            raise ValueError("data version must be between 0 and 1443")
        self = cls.from_component_data(_get_components(0))
        return self


class JavaChunk1444(Chunk):
    """
    Moved TerrainPopulated and LightPopulated to Status
    Made blocks paletted
    Added more tick tags
    Added structures tag
    """

    components = frozenset(_get_components(1444))

    @classmethod
    def new(cls, data_version: int) -> Self:
        if not 1444 <= data_version < 1466:
            raise ValueError("data version must be between 1444 and 1465")
        self = cls.from_component_data(_get_components(1444))
        return self


class JavaChunk1466(Chunk):
    """
    Added multiple height maps. Now stored in a compound.
    """

    components = frozenset(_get_components(1466))

    @classmethod
    def new(cls, data_version: int) -> Self:
        if not 1466 <= data_version < 2203:
            raise ValueError("data version must be between 1466 and 2202")
        self = cls.from_component_data(_get_components(1466))
        return self


class JavaChunk2203(Chunk):
    """
    Made biomes 3D
    """

    components = frozenset(_get_components(2203))

    @classmethod
    def new(cls, data_version: int) -> Self:
        if not 2203 <= data_version:
            raise ValueError("data version must be at least 2203")
        self = cls.from_component_data(_get_components(2203))
        return self


# TODO: Improve this if python/mypy#11673 gets fixed.
JavaChunk: TypeAlias = cast(UnionType, JavaChunkNA | JavaChunk0 | JavaChunk1444 | JavaChunk1466 | JavaChunk2203)

from typing import TYPE_CHECKING

import numpy
from amulet_nbt import NamedTag, ByteTag, ShortTag, IntTag, LongTag, FloatTag, DoubleTag, StringTag, CompoundTag, ListTag, ByteArrayTag, IntArrayTag, LongArrayTag

from amulet.utils.world_utils import encode_long_array

from amulet.chunk.components.height_2d import Height2DComponent

from amulet.level.java.anvil import RawChunkType
from amulet.level.java.chunk import JavaChunk

from amulet.level.java.chunk.components.raw_chunk import RawChunkComponent
from amulet.level.java.chunk.components.data_version import DataVersionComponent
from amulet.level.java.chunk.components.legacy_version import LegacyVersionComponent
from amulet.level.java.chunk.components.status import StatusComponent
from amulet.level.java.chunk.components.light_populated import LightPopulatedComponent
from amulet.level.java.chunk.components.terrain_populated import TerrainPopulatedComponent
from amulet.level.java.chunk.components.named_height_2d import NamedHeight2DComponent, NamedHeight2DData
from amulet.level.java.chunk.components.last_update import LastUpdateComponent
from amulet.level.java.chunk.components.inhabited_time import InhabitedTimeComponent

if TYPE_CHECKING:
    from ._level import JavaRawLevel
    from ._dimension import JavaRawDimension


def native_to_raw(
    raw_level: JavaRawLevel,
    dimension: JavaRawDimension,
    chunk: JavaChunk,
    cx: int,
    cz: int,
) -> RawChunkType:
    bounds = dimension.bounds().bounding_box()
    height = bounds.size_y

    # Get the data version. All Java chunk classes must have this
    data_version = chunk.get_component(DataVersionComponent)

    # Pull out or create the raw chunk data
    raw_chunk_component = chunk.get_component(RawChunkComponent)
    if raw_chunk_component is None:
        raw_chunk = {}
    else:
        raw_chunk = raw_chunk_component

    # Set up the region and level objects
    region = raw_chunk.setdefault("region", NamedTag()).compound
    if data_version >= 2844:
        # This should be unused
        level = CompoundTag()
    else:
        level = region.setdefault_compound("Level")

    if data_version >= 0:
        region["DataVersion"] = IntTag(data_version)
    else:
        region["V"] = ByteTag(chunk.get_component(LegacyVersionComponent))

    # Chunk x and y pos
    if data_version >= 2844:
        region["xPos"] = IntTag(cx)
        floor_cy = bounds.min_y >> 4
        region["yPos"] = IntTag(floor_cy)
        region["zPos"] = IntTag(cz)
    else:
        level["xPos"] = IntTag(cx)
        floor_cy = 0
        level["zPos"] = IntTag(cz)

    # LastUpdate
    if data_version >= 2844:
        region["LastUpdate"] = LongTag(chunk.get_component(LastUpdateComponent))
        region["InhabitedTime"] = LongTag(chunk.get_component(InhabitedTimeComponent))
    else:
        level["LastUpdate"] = LongTag(chunk.get_component(LastUpdateComponent))
        level["InhabitedTime"] = LongTag(chunk.get_component(InhabitedTimeComponent))

    # Status
    if data_version >= 2844:
        region["Status"] = StringTag(chunk.get_component(StatusComponent))
    elif data_version >= 1444:
        level["Status"] = StringTag(chunk.get_component(StatusComponent))
    else:
        level["TerrainPopulated"] = ByteTag(chunk.get_component(TerrainPopulatedComponent))
        level["LightPopulated"] = ByteTag(chunk.get_component(LightPopulatedComponent))

    # Height map
    if data_version >= 1466:
        height_maps = CompoundTag({
            key: LongArrayTag(
                encode_long_array(
                    value.ravel() - (floor_cy << 4),
                    height.bit_length(),
                    data_version <= 2529,
                )
            )
            for key, value in chunk.get_component(NamedHeight2DComponent).arrays.items()
            if isinstance(key, str) and isinstance(value, numpy.ndarray) and value.size == 256
        })
        if data_version >= 2844:
            region["HeightMaps"] = height_maps
        else:
            level["HeightMaps"] = height_maps
    else:
        level["HeightMap"] = IntArrayTag(chunk.get_component(Height2DComponent).ravel())

    return raw_chunk

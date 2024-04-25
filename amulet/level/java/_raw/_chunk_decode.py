from typing import TYPE_CHECKING

import numpy
from amulet_nbt import (
    NamedTag,
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    FloatTag,
    DoubleTag,
    StringTag,
    CompoundTag,
    ListTag,
    ByteArrayTag,
    IntArrayTag,
    LongArrayTag,
)

from amulet.block import Block, BlockStack
from amulet.biome import Biome
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.version import VersionNumber, VersionRange
from amulet.chunk import ComponentDataMapping
from amulet.chunk.components.height_2d import Height2DComponent
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

from amulet.utils.world_utils import decode_long_array

from amulet.level.java.anvil import RawChunkType
from amulet.level.java.chunk import (
    JavaChunk,
    JavaChunkNA,
    JavaChunk0,
    JavaChunk1444,
    JavaChunk1466,
    JavaChunk2203,
)

from amulet.level.java.chunk.components.raw_chunk import RawChunkComponent
from amulet.level.java.chunk.components.data_version import DataVersionComponent
from amulet.level.java.chunk.components.legacy_version import LegacyVersionComponent
from amulet.level.java.chunk.components.status import StatusComponent
from amulet.level.java.chunk.components.light_populated import LightPopulatedComponent
from amulet.level.java.chunk.components.terrain_populated import (
    TerrainPopulatedComponent,
)
from amulet.level.java.chunk.components.named_height_2d import (
    NamedHeight2DComponent,
    NamedHeight2DData,
)
from amulet.level.java.chunk.components.last_update import LastUpdateComponent
from amulet.level.java.chunk.components.inhabited_time import InhabitedTimeComponent

if TYPE_CHECKING:
    from ._level import JavaRawLevel
    from ._dimension import JavaRawDimension


def raw_to_native(
    raw_level: JavaRawLevel,
    dimension: JavaRawDimension,
    raw_chunk: RawChunkType,
    cx: int,
    cz: int,
) -> JavaChunk:
    floor_y = dimension.bounds().min_y
    ceil_y = dimension.bounds().max_y
    height_y = ceil_y - floor_y

    # Init the chunk components
    chunk_components: ComponentDataMapping = {}  # type: ignore
    # Raw chunk data
    chunk_components[RawChunkComponent] = raw_chunk

    # Get the region object
    region = raw_chunk.get("region", NamedTag()).compound
    # Get the level object. This may not exist.
    level = region.get_compound("Level", CompoundTag())

    # Pull out the data version
    chunk_components[DataVersionComponent] = data_version = region.pop_int(
        "DataVersion", IntTag(-1)
    ).py_int
    version_range = VersionRange("java", VersionNumber(data_version), VersionNumber(data_version))

    # Get the chunk class
    chunk_class: type[JavaChunk]
    if data_version >= 2203:
        chunk_class = JavaChunk2203
    elif data_version >= 1466:
        chunk_class = JavaChunk1466
    elif data_version >= 1444:
        chunk_class = JavaChunk1444
    elif data_version >= 0:
        chunk_class = JavaChunk0
    else:
        chunk_class = JavaChunkNA

    if data_version == -1:
        chunk_components[LegacyVersionComponent] = level.pop_byte(
            "V", ByteTag(1)
        ).py_int

    # Chunk x and y pos
    if data_version >= 2844:
        assert region.pop_int("xPos") == IntTag(cx)
        floor_cy = region.pop_int("yPos", IntTag(0)).py_int << 4
        assert region.pop_int("zPos") == IntTag(cz)
    else:
        assert level.pop_int("xPos") == IntTag(cx)
        floor_cy = 0
        assert level.pop_int("zPos") == IntTag(cz)

    # LastUpdate and InhabitedTime
    if data_version >= 2844:
        chunk_components[LastUpdateComponent] = region.pop_long(
            "LastUpdate", LongTag(0)
        ).py_int
        chunk_components[InhabitedTimeComponent] = region.pop_long(
            "InhabitedTime", LongTag(0)
        ).py_int
    else:
        chunk_components[LastUpdateComponent] = level.pop_long(
            "LastUpdate", LongTag(0)
        ).py_int
        chunk_components[InhabitedTimeComponent] = level.pop_long(
            "InhabitedTime", LongTag(0)
        ).py_int

    # Status
    if data_version >= 1444:
        if data_version >= 2844:
            status = region.pop_string("Status")
        else:
            status = level.pop_string("Status")

        if status is not None:
            chunk_components[StatusComponent] = status.py_str
        elif data_version >= 3454:
            chunk_components[StatusComponent] = "minecraft:full"
        elif data_version >= 1912:
            chunk_components[StatusComponent] = "full"
        else:
            chunk_components[StatusComponent] = "postprocessed"
    else:
        chunk_components[TerrainPopulatedComponent] = bool(
            level.pop_byte("TerrainPopulated", ByteTag(1))
        )
        chunk_components[LightPopulatedComponent] = bool(
            level.pop_byte("LightPopulated", ByteTag(1))
        )

    # Height map
    if data_version >= 1466:
        if data_version >= 2844:
            heights = region.pop_compound("HeightMaps", CompoundTag())
        else:
            heights = level.pop_compound("HeightMaps", CompoundTag())
        arrays: dict[str, numpy.ndarray] = {}
        for key, value in heights.items():
            if isinstance(key, str) and isinstance(value, LongArrayTag):
                arrays[key] = decode_long_array(
                    value.np_array,
                    256,
                    height_y.bit_length(),
                    dense=data_version <= 2529,
                ).reshape((16, 16)) + (floor_cy << 4)
        chunk_components[NamedHeight2DComponent] = NamedHeight2DData((16, 16), arrays)
    else:
        height = level.pop_int_array("HeightMap")
        if isinstance(height, IntArrayTag) and len(height) == 256:
            chunk_components[Height2DComponent] = height.np_array.astype(
                numpy.int64
            ).reshape((16, 16))
        else:
            chunk_components[Height2DComponent] = numpy.zeros((16, 16), numpy.int64)

    # block entities
    if data_version >= 2844:
        # region.block_entities
        block_entities = region.pop_list("block_entities", ListTag())
    else:
        # region.Level.TileEntities
        block_entities = level.pop_list("TileEntities", ListTag())
    chunk_components[BlockEntityComponent] = block_entity_component = BlockEntityComponentData(version_range)
    for tag in block_entities:
        if not isinstance(tag, CompoundTag):
            continue

        entity_id = tag.pop_string("id", raise_errors=True)
        namespace, base_name = entity_id.py_str.split(":", 1)
        x = tag.pop_int("x", raise_errors=True).py_int
        y = tag.pop_int("y", raise_errors=True).py_int
        z = tag.pop_int("z", raise_errors=True).py_int

        block_entity_component[(x, y, z)] = BlockEntity("java", VersionNumber(data_version), namespace, base_name, NamedTag(tag))

    # entities
    entities = ListTag()
    if data_version >= 2681:
        # It seems like the inline version can exist at the same time as the external format.
        # entities.Entities
        entity_layer = raw_chunk.get("entities", NamedTag()).compound
        assert entity_layer.get_int("DataVersion", IntTag(data_version)).py_int == data_version, "data version mismatch."
        entities.extend(entity_layer.pop_list("Entities", ListTag()))
    if data_version >= 2844:
        # region.entities
        entities.extend(region.pop_list("entities"))
    else:
        # region.Level.Entities
        entities.extend(level.pop_list("Entities"))
    chunk_components[EntityComponent] = entity_component = EntityComponentData(version_range)
    for tag in entities:
        if not isinstance(tag, CompoundTag):
            continue

        entity_id = tag.pop_string("id", raise_errors=True)
        namespace, base_name = entity_id.py_str.split(":", 1)
        pos = tag.pop_list("Pos", raise_errors=True)
        x = pos[0].py_float
        y = pos[1].py_float
        z = pos[2].py_float
        entity_component.add(Entity("java", VersionNumber(data_version), namespace, base_name, x, y, z, NamedTag(tag)))

    return chunk_class.from_component_data(chunk_components)
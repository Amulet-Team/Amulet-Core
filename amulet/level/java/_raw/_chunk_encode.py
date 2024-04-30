from typing import TYPE_CHECKING, Callable
from functools import cache
import logging

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

from amulet.game import get_game_version
from amulet.utils.world_utils import encode_long_array

from amulet.block import Block, BlockStack
from amulet.biome import Biome
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.version import VersionNumber, VersionRange

from amulet.chunk.components.height_2d import Height2DComponent
from amulet.chunk.components.biome import (
    Biome2DComponent,
    Biome2DComponentData,
    Biome3DComponent,
    Biome3DComponentData,
)
from amulet.chunk.components.block import BlockComponent, BlockComponentData
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer
from amulet.chunk.components.block_entity import (
    BlockEntityComponent,
    BlockEntityComponentData,
)
from amulet.chunk.components.entity import EntityComponent, EntityComponentData

from amulet.level.java.anvil import RawChunkType
from amulet.level.java.chunk import JavaChunk

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


log = logging.getLogger(__name__)


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
    game_version = get_game_version("java", VersionNumber(data_version))

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
        ceil_cy = bounds.max_y >> 4
        region["zPos"] = IntTag(cz)
    else:
        level["xPos"] = IntTag(cx)
        floor_cy = 0
        ceil_cy = 16
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
        level["TerrainPopulated"] = ByteTag(
            chunk.get_component(TerrainPopulatedComponent)
        )
        level["LightPopulated"] = ByteTag(chunk.get_component(LightPopulatedComponent))

    # Height map
    if data_version >= 1466:
        height_maps = CompoundTag(
            {
                key: LongArrayTag(
                    encode_long_array(
                        value.ravel() - (floor_cy << 4),
                        height.bit_length(),
                        data_version <= 2529,
                    )
                )
                for key, value in chunk.get_component(
                    NamedHeight2DComponent
                ).arrays.items()
                if isinstance(key, str)
                and isinstance(value, numpy.ndarray)
                and value.size == 256
            }
        )
        if data_version >= 2844:
            region["HeightMaps"] = height_maps
        else:
            level["HeightMaps"] = height_maps
    else:
        level["HeightMap"] = IntArrayTag(chunk.get_component(Height2DComponent).ravel())

    # biomes
    get_biome_id_override: Callable[[str, str], int] = raw_level.biome_id_override.namespace_id_to_numerical_id
    get_biome_id_game: Callable[[str, str], int] = game_version.biome.namespace_id_to_numerical_id

    @cache
    def encode_biome(namespace: str, base_name: str) -> int:
        try:
            # First try overrides
            return get_biome_id_override(namespace, base_name)
        except KeyError:
            try:
                # Then fall back to the game implementation.
                return get_biome_id_game(namespace, base_name)
            except KeyError:
                log.error(
                    f"Unknown biome {namespace}:{base_name}. Falling back to default."
                )
                default_biome = dimension.default_biome()
                if (
                    namespace == default_biome.namespace
                    and base_name == default_biome.base_name
                ):
                    return 0
                return encode_biome(default_biome.namespace, default_biome.base_name)

    if data_version >= 2844:
        sections = region.setdefault_list("sections")
    else:
        sections = level.setdefault_list("sections")
    sections_map = {}
    for section in sections:
        assert isinstance(section, CompoundTag)
        sections_map[section.get_byte("Y", raise_errors=True).py_int] = section

    if data_version >= 2203:
        # 3D
        biome_data_3d: Biome3DComponentData = chunk.get_component(Biome3DComponent)
        biome_sections: SubChunkArrayContainer = biome_data_3d.sections
        palette = biome_data_3d.palette
        if data_version >= 2836:
            # Paletted
            # if data_version >= 2844:
            #     # region.sections[].biomes.palette
            #     # region.sections[].biomes.data
            # else:
            #     # region.Level.sections[].biomes.palette
            #     # region.Level.sections[].biomes.data

            for cy in range(floor_cy, ceil_cy):
                if cy not in biome_sections:
                    continue
                arr = numpy.transpose(
                    biome_sections[cy], (1, 2, 0)
                ).ravel()
                runtime_ids, arr = numpy.unique(
                    arr, return_inverse=True
                )
                sub_palette = ListTag([
                    StringTag(palette.index_to_biome(runtime_id).namespaced_name)
                    for runtime_id in runtime_ids
                ])
                section = sections_map.get(cy, None)
                if section is None:
                    section = sections_map[cy] = CompoundTag()
                    sections.append(section)
                biomes = section["biomes"] = CompoundTag({"palette": sub_palette})
                if len(sub_palette) > 1:
                    biomes["data"] = LongArrayTag(
                        encode_long_array(arr, dense=data_version <= 2529)
                    )
        else:
            # hard coded ids
            # region.Level.Biomes (4x64x4 IntArrayTag[1024])
            arrays = []
            for cy in range(floor_cy, ceil_cy):
                if cy not in biome_sections:
                    biome_sections.populate(cy)
                arrays.append(biome_sections[cy])
            arr = numpy.transpose(
                numpy.stack(arrays, 1, dtype=numpy.uint32),
                (1, 2, 0),
            ).ravel()  # YZX -> XYZ
            runtime_ids, arr = numpy.unique(arr, return_inverse=True)
            numerical_ids = []
            for rid in runtime_ids:
                biome = palette.index_to_biome(rid)
                numerical_ids.append(encode_biome(biome.namespace, biome.base_name))
            level["Biomes"] = IntArrayTag(
                numpy.asarray(numerical_ids, dtype=numpy.uint32)[arr]
            )
    else:
        # 2D
        biome_data_2d: Biome2DComponentData = chunk.get_component(Biome2DComponent)
        runtime_ids, arr = numpy.unique(
            biome_data_2d.array.ravel(), return_inverse=True
        )
        numerical_ids = []
        for rid in runtime_ids:
            biome = biome_data_2d.palette.index_to_biome(rid)
            numerical_ids.append(encode_biome(biome.namespace, biome.base_name))
        if data_version >= 1467:
            # region.Level.Biomes (16x16 IntArrayTag[256])
            level["Biomes"] = IntArrayTag(
                numpy.asarray(numerical_ids, dtype=numpy.uint32)[arr]
            )
        else:
            # region.Level.Biomes (16x16 ByteArrayTag[256])
            level["Biomes"] = ByteArrayTag(
                numpy.asarray(numerical_ids, dtype=numpy.uint8)[arr]
            )
    # block entities
    block_entities = ListTag()
    block_entity: BlockEntity
    for (x, y, z), block_entity in chunk.get_component(BlockEntityComponent).items():
        tag = block_entity.nbt.compound
        tag["id"] = StringTag(block_entity.namespaced_name)
        tag["x"] = IntTag(x)
        tag["y"] = IntTag(y)
        tag["z"] = IntTag(z)
        block_entities.append(tag)
    if data_version >= 2844:
        # region.block_entities
        region["block_entities"] = block_entities
    else:
        # region.Level.TileEntities
        level["TileEntities"] = block_entities

    # entities
    entities = ListTag()
    entity: Entity
    for entity in chunk.get_component(EntityComponent):
        tag = entity.nbt.compound
        tag["id"] = StringTag(entity.namespaced_name)
        tag["Pos"] = ListTag(
            [DoubleTag(entity.x), DoubleTag(entity.y), DoubleTag(entity.z)]
        )
        entities.append(tag)
    if data_version >= 2681:
        # entities.Entities
        entity_layer = raw_chunk.setdefault("entities", NamedTag()).compound
        entity_layer["Entities"] = entities
    else:
        # region.Level.Entities
        level["Entities"] = entities

    return raw_chunk

from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from functools import cache
import logging

import numpy
from amulet_nbt import (
    NamedTag,
    AbstractBaseIntTag,
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
from amulet.game.java import JavaGameVersion, Waterloggable
from amulet.utils.world_utils import encode_long_array, to_nibble_array
from amulet.utils.numpy import unique_inverse

from amulet.block import Block, BlockStack
from amulet.biome import Biome
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.version import VersionNumber, VersionRange
from amulet.palette import BlockPalette

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
    get_biome_id_override: Callable[[str, str], int] = (
        raw_level.biome_id_override.namespace_id_to_numerical_id
    )
    get_biome_id_game: Callable[[str, str], int] = (
        game_version.biome.namespace_id_to_numerical_id
    )

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
        # region.sections[]
        sections_tag = region.setdefault_list("sections")
    else:
        # region.Level.sections[]
        sections_tag = level.setdefault_list("sections")
    sections_map = {}
    for section_tag in sections_tag:
        assert isinstance(section_tag, CompoundTag)
        sections_map[section_tag.get_byte("Y", ByteTag(0)).py_int] = section_tag

    def get_section(cy_: int) -> CompoundTag:
        section_tag_ = sections_map.get(cy_, None)
        if section_tag_ is None:
            section_tag_ = sections_map[cy_] = CompoundTag()
            section_tag_["Y"] = ByteTag(cy_)
            sections_tag.append(section_tag_)
        return section_tag_

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
                arr = numpy.transpose(biome_sections[cy], (1, 2, 0)).ravel()
                runtime_ids, arr = numpy.unique(arr, return_inverse=True)
                sub_palette = ListTag(
                    [
                        StringTag(palette.index_to_biome(runtime_id).namespaced_name)
                        for runtime_id in runtime_ids
                    ]
                )
                section_tag = get_section(cy)
                biomes = section_tag["biomes"] = CompoundTag({"palette": sub_palette})
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

    # blocks
    block_component_data = chunk.get_component(BlockComponent)
    block_palette: BlockPalette = block_component_data.palette
    block_sections: SubChunkArrayContainer = block_component_data.sections

    if data_version >= 1444:
        # if data_version >= 2844:
        #     # region.sections[].block_states.data
        #     # region.sections[].block_states.palette
        # elif data_version >= 2836:
        #     # region.Level.Sections[].block_states.data
        #     # region.Level.Sections[].block_states.palette
        # else:
        #     # region.Level.Sections[].BlockStates
        #     # region.Level.Sections[].Palette
        for cy, block_section in block_sections.items():
            if floor_cy <= cy <= ceil_cy:
                block_sub_array = numpy.transpose(block_section, (1, 2, 0)).ravel()
                block_lut, block_arr = unique_inverse(block_sub_array)
                palette_tag = ListTag[CompoundTag]()
                for palette_index in block_lut:
                    palette_tag.append(
                        encode_block(
                            game_version,
                            block_palette.index_to_block_stack(palette_index),
                        )
                    )

                section_tag = get_section(cy)
                if data_version >= 2836:
                    section_tag["block_states"] = block_states_tag = CompoundTag(
                        {"palette": palette_tag}
                    )
                    if len(palette_tag) > 1:
                        block_states_tag["data"] = LongArrayTag(
                            encode_long_array(
                                block_sub_array,
                                dense=data_version <= 2529,
                                min_bits_per_entry=4,
                            )
                        )
                else:
                    section_tag["Palette"] = palette_tag
                    section_tag["BlockStates"] = LongArrayTag(
                        encode_long_array(
                            block_sub_array,
                            dense=data_version <= 2529,
                            min_bits_per_entry=4,
                        )
                    )
    else:
        # region.Level.Sections[].Blocks
        # region.Level.Sections[].Add
        # region.Level.Sections[].Data
        get_block_id_override = raw_level.block_id_override.namespace_id_to_numerical_id
        get_block_id_game = game_version.block.namespace_id_to_numerical_id
        block_ids = []
        block_datas = []
        for block_stack in block_palette:
            block = block_stack[0]
            namespace = block.namespace
            base_name = block.base_name
            try:
                block_id = get_block_id_override(namespace, base_name)
            except KeyError:
                try:
                    block_id = get_block_id_game(namespace, base_name)
                except KeyError:
                    if namespace == "numerical" and base_name.isnumeric():
                        block_id = int(base_name) & 255
                    else:
                        block_id = 0

            block_data_tag = block.properties.get("block_data")
            if isinstance(block_data_tag, AbstractBaseIntTag):
                block_data = block_data_tag.py_int & 15
            else:
                block_data = 0
            block_ids.append(block_id)
            block_datas.append(block_data)
        block_id_array = numpy.array(block_ids, dtype=numpy.uint8)
        block_data_array = numpy.array(block_datas, dtype=numpy.uint8)

        for cy, block_section in block_sections.items():
            if 0 <= cy <= 16:
                flat_block_section = numpy.transpose(
                    block_section, (1, 2, 0)
                ).ravel()  # XYZ -> YZX
                section_tag = get_section(cy)
                section_tag["Blocks"] = ByteArrayTag(block_id_array[flat_block_section])
                section_tag["Data"] = ByteArrayTag(
                    to_nibble_array(block_data_array[flat_block_section])
                )

    # block entities
    block_entities = ListTag[CompoundTag]()
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
    entities = ListTag[CompoundTag]()
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

    if 1519 <= data_version < 1901:
        # all defined sections must have the BlockStates and Palette fields
        for section in sections_map.values():
            if "Palette" in section:
                if "BlockStates" not in section:
                    assert len(section.get_list("Palette", raise_errors=True)) == 1
                    section["BlockStates"] = LongArrayTag([0] * 256)
            else:
                section["Palette"] = ListTag(
                    [CompoundTag({"Name": StringTag("minecraft:air")})]
                )
                section["BlockStates"] = LongArrayTag([0] * 256)

    if data_version < 1934:
        # BlockLight and SkyLight are required
        for section_tag in sections_map.values():
            for key in ("BlockLight", "SkyLight"):
                if key not in section_tag:
                    section_tag[key] = ByteArrayTag(
                        numpy.full(2048, 255, dtype=numpy.uint8)
                    )

    return raw_chunk


def encode_block(game_version: JavaGameVersion, block_stack: BlockStack) -> CompoundTag:
    base_block = block_stack[0]
    namespace = base_block.namespace
    base_name = base_block.base_name
    properties = dict(base_block.properties)
    block_tag = CompoundTag({"Name": StringTag(f"{namespace}:{base_name}")})
    if game_version.block.waterloggable(namespace, base_name) == Waterloggable.Yes:
        if (
            len(block_stack) >= 2
            and block_stack[1].namespaced_name == "minecraft:water"
        ):
            properties["waterlogged"] = StringTag("true")
        else:
            properties["waterlogged"] = StringTag("false")
    if properties:
        string_properties = {
            k: v for k, v in properties.items() if isinstance(v, StringTag)
        }
        if string_properties:
            block_tag["Properties"] = CompoundTag(string_properties)
    return block_tag

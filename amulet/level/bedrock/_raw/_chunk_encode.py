from __future__ import annotations
import struct
from typing import TYPE_CHECKING, Callable, Iterable
from functools import cache

import numpy

from amulet_nbt import (
    CompoundTag,
    ShortTag,
    IntTag,
    FloatTag,
    StringTag,
    ListTag,
    NamedTag,
    utf8_escape_encoding,
)

from amulet.block import Block, BlockStack, PropertyType, PropertyValueClasses
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.biome import Biome
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer
from amulet.chunk.components.block import BlockComponent
from amulet.chunk.components.block_entity import (
    BlockEntityComponent,
    BlockEntityContainer,
)
from amulet.chunk.components.entity import EntityComponent, EntityContainer
from amulet.chunk.components.height_2d import Height2DComponent
from amulet.chunk.components.biome import Biome2DComponent, Biome3DComponent
from amulet.game import get_game_version
from amulet.version import VersionNumber
from amulet.palette import BlockPalette

from amulet.level.bedrock._raw import BedrockRawChunk
from amulet.level.bedrock.chunk import BedrockChunk
from amulet.level.bedrock.chunk.components.finalised_state import (
    FinalisedStateComponent,
)
from amulet.level.bedrock.chunk.components.raw_chunk import RawChunkComponent
from amulet.level.bedrock.chunk.components.chunk_version import ChunkVersionComponent

if TYPE_CHECKING:
    from ._level import BedrockRawLevel
    from ._dimension import BedrockRawDimension


@cache
def pack_block_version(version: VersionNumber) -> int:
    return struct.unpack(">i", bytes([*version.padded_version(4)]))[0]  # type: ignore


def native_to_raw(
    raw_level: BedrockRawLevel, dimension: BedrockRawDimension, chunk: BedrockChunk
) -> BedrockRawChunk:
    game_version = get_game_version("bedrock", raw_level.version)
    max_version = game_version.max_version

    floor_cy = dimension.bounds().min_y >> 4
    ceil_cy = dimension.bounds().max_y >> 4

    if isinstance(chunk, RawChunkComponent) and chunk.raw_chunk is not None:
        raw_chunk = chunk.raw_chunk
    else:
        raw_chunk = BedrockRawChunk()
    chunk_data = raw_chunk.chunk_data

    if isinstance(chunk, ChunkVersionComponent):
        chunk_version = chunk.chunk_version
        chunk_data[b"v" if chunk.chunk_version <= 20 else b","] = bytes([chunk_version])
    else:
        raise RuntimeError

    if isinstance(chunk, FinalisedStateComponent):
        if max_version >= VersionNumber(1):
            # TODO: when did this become an int?
            chunk_data[b"\x36"] = struct.pack("<i", chunk.finalised_state)
        else:
            chunk_data[b"\x36"] = struct.pack("b", chunk.finalised_state)

    if isinstance(chunk, BlockComponent):
        terrain: dict[int, bytes]
        if max_version >= VersionNumber(1, 17, 30):
            terrain = _encode_blocks_v9(
                chunk, floor_cy, ceil_cy, dimension.default_block()[0]
            )
        elif max_version >= VersionNumber(1, 3):
            terrain = _encode_blocks_v8(
                chunk, floor_cy, ceil_cy, dimension.default_block()[0]
            )
        elif max_version >= VersionNumber(0, 17):
            terrain = _encode_blocks_v1(
                chunk, dimension.default_block()[0]
            )
        else:
            terrain = _encode_blocks_v0(chunk)

        # TODO: is this right?
        for cy, sub_chunk in terrain.items():
            if 25 <= chunk_version <= 28:
                # The chunk db keys all start at 0 regardless of chunk floor position.
                # This is the floor position of when the world was created.
                # If the floor position changes in the future this will break.
                chunk_key = struct.pack("b", cy - floor_cy)
            else:
                chunk_key = struct.pack("b", cy)

            chunk_data[b"\x2F" + chunk_key] = sub_chunk

    if isinstance(chunk, Height2DComponent) and chunk.height is not None:
        height = chunk.height.ravel().astype("<i2").tobytes()
    else:
        height = bytes(512)

    if isinstance(chunk, Biome2DComponent):
        biomes_array = chunk.biomes.astype("uint8").T.tobytes()
        chunk_data[b"\x2D"] = height + biomes_array

    elif isinstance(chunk, Biome3DComponent):
        d2d: list[bytes] = [height]

        biomes: SubChunkArrayContainer = chunk.biomes

        highest = next(
            (cy for cy in range(ceil_cy, floor_cy - 1, -1) if cy in biomes), None
        )
        if highest is None:
            # populate the lowest array
            biomes.populate(floor_cy)
        else:
            for cy in range(highest - 1, floor_cy - 1, -1):
                if cy not in biomes:
                    biomes.populate(cy)

        for cy in range(floor_cy, floor_cy + 25):
            if cy in biomes:
                arr = biomes[cy]
                palette, arr_uniq = numpy.unique(arr, return_inverse=True)
                if len(palette) == 1:
                    d2d.append(b"\x01")
                else:
                    d2d.append(_encode_packed_array(arr_uniq.reshape(arr.shape)))
                    d2d.append(struct.pack("<I", len(palette)))
                d2d.append(palette.astype("<i4").tobytes())
            else:
                d2d.append(b"\xFF")

        chunk_data[b"+"] = b"".join(d2d)

    if isinstance(chunk, BlockEntityComponent):
        block_entities_out = _encode_block_entities(chunk.block_entities)
        if block_entities_out:
            chunk_data[b"\x31"] = _pack_nbt_list(block_entities_out)

    if isinstance(chunk, EntityComponent):
        entities_out = _encode_entities(chunk.entities, max_version >= VersionNumber(1, 8))
        if entities_out:
            if max_version >= VersionNumber(1, 18, 30):
                raw_chunk.entity_actor.extend(entities_out)
            else:
                chunk_data[b"\x32"] = _pack_nbt_list(entities_out)

    return raw_chunk


def _encode_blocks_v0(chunk: BlockComponent) -> dict[int, bytes]:
    raise NotImplementedError


@cache
def _encode_block(block: Block) -> NamedTag:
    """Encode a block to its NameTag form.

    Note that this may return a cached result. Do not modify the returned value.

    :param block: The block to encode
    :return: The encoded block.
    """
    if block.version >= VersionNumber(1, 13):  # This version may be wrong
        # block with block state
        return NamedTag(
            CompoundTag(
                {
                    "name": StringTag(block.namespaced_name),
                    "states": CompoundTag(
                        {
                            key: val
                            for key, val in block.properties.items()
                            if isinstance(val, PropertyValueClasses)
                        }
                    ),
                    "version": IntTag(pack_block_version(block.version)),
                }
            )
        )
    else:
        # block with block data
        block_data = block.properties.get("block_data", IntTag(0))
        if isinstance(block_data, IntTag):
            block_data_int = block_data.py_int
        else:
            block_data_int = 0
        return NamedTag(
            CompoundTag(
                {
                    "name": StringTag(block.namespaced_name),
                    "val": ShortTag(block_data_int),
                }
            )
        )


def _encode_block_palette(
    block_palette: BlockPalette, default_block: Block, max_block_depth: int
) -> list[tuple[list[NamedTag], numpy.ndarray]]:
    """Encode the block palette.

    Remove duplicates from each layer of the palette.
    Return the encoded block palette and a numpy index array to remap the old block array.

    :param block_palette: The block palette to encode.
    :param default_block: The default block to use in extra layers where the block stack is not long enough.
    :param max_block_depth: The maximum block depth to process.
    :return: The encoded block palette and numpy inverse array for each layer.
    """
    block: Block | None

    # Transpose the block palette
    block_layers: list[list[Block | None]] = [
        [None] * len(block_palette) for _ in range(max_block_depth)
    ]
    for block_index, block_stack in enumerate(block_palette):
        for block_layer, block in enumerate(block_stack):
            if block_layer < max_block_depth:
                block_layers[block_layer][block_index] = block

    # Crop layers without extra blocks
    block_layers = block_layers[
        : next(
            (
                i + 1
                for i in range(len(block_layers) - 1, 0, -1)
                if any(block_layers[i])
            ),
            1,
        )
    ]

    compact_layers: list[tuple[list[NamedTag], numpy.ndarray]] = []

    for layer in block_layers:
        compact_palette_lut: dict[Block, int] = {}
        encoded_palette: list[NamedTag] = []
        remap: list[int] = []
        for block in layer:
            if block is None:
                block = default_block
            palette_index = compact_palette_lut.get(block)
            if palette_index is None:
                palette_index = len(compact_palette_lut)
                compact_palette_lut[block] = palette_index
                encoded_palette.append(_encode_block(block))
            remap.append(palette_index)

        compact_layers.append((encoded_palette, numpy.array(remap)))

    return compact_layers


def _encode_block_palette_layer(
    layer_palette: list[NamedTag],
    layer_palette_lut: numpy.ndarray,
    palette_lut: numpy.ndarray,
    unique_block_array: numpy.ndarray,
) -> bytes:
    """Encode one palettised layer.

    The two look up tables are so that the unique can be computed once per sub-chunk rather than once per layer.

    :param layer_palette: The encoded block palette. This may contain unused values. All values must be unique.
    :param layer_palette_lut: A LUT mapping from the original block palette to the compacted palette for this layer.
    :param palette_lut: A LUT mapping from the unique block array to the original block palette.
    :param unique_block_array: The block array containing only unique values.
    :return: The encoded bytes
    """
    # merge the luts
    lut = layer_palette_lut[palette_lut]
    # compute the unique. This is faster than computing the unique for the whole array for each layer.
    palette_indexes, lut = numpy.unique(lut, return_inverse=True)

    unique_layer_palette = [layer_palette[i] for i in palette_indexes]
    block_array = lut[unique_block_array]

    return b"".join(
        (
            _encode_packed_array(block_array.reshape((16, 16, 16))),
            struct.pack("<I", len(unique_layer_palette)),
            *[
                block.save_to(
                    compressed=False,
                    little_endian=True,
                    string_encoding=utf8_escape_encoding,
                )
                for block in unique_layer_palette
            ],
        )
    )


def _encode_palettized_chunk(
    chunk: BlockComponent,
    min_cy: int,
    max_cy: int,
    default_block: Block,
    max_block_depth: int,
) -> dict[int, list[bytes]]:
    """Encode the palettized sections of the chunk data. The caller handles the header."""
    blocks: SubChunkArrayContainer = chunk.blocks
    block_palette: BlockPalette = chunk.block_palette
    encoded_block_palette = _encode_block_palette(
        block_palette, default_block, max_block_depth
    )

    encoded = {}
    for cy in range(min_cy, max_cy):
        if cy in blocks:
            block_lut, block_arr = numpy.unique(blocks[cy], return_inverse=True)
            encoded[cy] = [
                _encode_block_palette_layer(
                    layer_palette, layer_palette_lut, block_lut, block_arr
                )
                for layer_palette, layer_palette_lut in encoded_block_palette
            ]
    return encoded


def _encode_blocks_v1(
    chunk: BlockComponent, default_block: Block
) -> dict[int, bytes]:
    return {
        cy: b"".join((b"\x01", *layers))
        for cy, layers in _encode_palettized_chunk(
            chunk, 0, 16, default_block, 1
        ).items()
    }


def _encode_blocks_v8(
    chunk: BlockComponent, min_cy: int, max_cy: int, default_block: Block
) -> dict[int, bytes]:
    return {
        cy: b"".join((b"\x08", struct.pack("b", len(layers)), *layers))
        for cy, layers in _encode_palettized_chunk(
            chunk, min_cy, max_cy, default_block, 2
        ).items()
    }


def _encode_blocks_v9(
    chunk: BlockComponent, min_cy: int, max_cy: int, default_block: Block
) -> dict[int, bytes]:
    return {
        cy: b"".join((b"\x09", struct.pack("bb", len(layers), cy), *layers))
        for cy, layers in _encode_palettized_chunk(
            chunk, min_cy, max_cy, default_block, 2
        ).items()
    }


def _encode_packed_array(arr: numpy.ndarray, min_bit_size: int = 1) -> bytes:
    bits_per_value = max(int(numpy.amax(arr)).bit_length(), min_bit_size)
    if bits_per_value == 7:
        bits_per_value = 8
    elif 9 <= bits_per_value <= 15:
        bits_per_value = 16
    header = bytes([bits_per_value << 1])

    values_per_word = 32 // bits_per_value  # Word = 4 bytes, basis of compacting.
    word_count = -(-4096 // values_per_word)  # Ceiling divide is inverted floor divide

    arr = arr.swapaxes(1, 2).ravel()
    packed_arr = bytes(
        reversed(
            numpy.packbits(
                numpy.pad(
                    numpy.pad(
                        numpy.unpackbits(
                            numpy.ascontiguousarray(arr[::-1], dtype=">i").view(
                                dtype="uint8"
                            )
                        ).reshape(4096, -1)[:, -bits_per_value:],
                        [(word_count * values_per_word - 4096, 0), (0, 0)],
                        "constant",
                    ).reshape(-1, values_per_word * bits_per_value),
                    [(0, 0), (32 - values_per_word * bits_per_value, 0)],
                    "constant",
                )
            )
            .view(dtype=">i4")
            .tobytes()
        )
    )
    return header + packed_arr


def _pack_nbt_list(nbt_list: list[NamedTag]) -> bytes:
    return b"".join(
        [
            nbt.save_to(
                compressed=False,
                little_endian=True,
                string_encoding=utf8_escape_encoding,
            )
            for nbt in nbt_list
        ]
    )


def _encode_entities(entities: EntityContainer, str_id: bool) -> list[NamedTag]:
    entities_out = []
    for entity in entities:
        nbt = _encode_entity(entity, str_id)
        if nbt is not None:
            entities_out.append(nbt)

    return entities_out


def _encode_entity(entity: Entity, str_id: bool) -> NamedTag | None:
    named_tag = entity.nbt
    tag = named_tag.tag
    if not isinstance(tag, CompoundTag):
        return None

    if str_id:
        tag["identifier"] = StringTag(entity.namespaced_name)
    else:
        if not entity.base_name.isnumeric():
            return None
        tag["id"] = IntTag(int(entity.base_name))

    tag["Pos"] = ListTag(
        [
            FloatTag(float(entity.x)),
            FloatTag(float(entity.y)),
            FloatTag(float(entity.z)),
        ]
    )
    return named_tag


def _encode_block_entities(block_entities: BlockEntityContainer) -> list[NamedTag]:
    entities_out = []
    for location, block_entity in block_entities.items():
        nbt = _encode_block_entity(location, block_entity)
        if nbt is not None:
            entities_out.append(nbt)
    return entities_out


def _encode_block_entity(
    location: tuple[int, int, int], block_entity: BlockEntity
) -> NamedTag | None:
    named_tag = block_entity.nbt
    tag = named_tag.tag
    if not isinstance(tag, CompoundTag):
        return None
    tag["id"] = StringTag(block_entity.base_name)
    tag["x"] = IntTag(location[0])
    tag["y"] = IntTag(location[1])
    tag["z"] = IntTag(location[2])
    return named_tag

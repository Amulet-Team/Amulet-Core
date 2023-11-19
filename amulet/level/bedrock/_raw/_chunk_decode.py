from __future__ import annotations
import struct
from typing import Optional, TypeVar, Any, TYPE_CHECKING
import logging
from functools import cache

import numpy

from amulet_nbt import (
    CompoundTag,
    IntTag,
    StringTag,
    ListTag,
    NamedTag,
    ReadContext,
    load_array as load_nbt_array,
    load as load_nbt,
    utf8_escape_decoder,
)

from amulet.block import Block, BlockStack, PropertyType, PropertyDataTypes
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.chunk.components.block import BlockComponent
from amulet.chunk.components.block_entity import BlockEntityComponent
from amulet.chunk.components.entity import EntityComponent
from amulet.chunk.components.height_2d import Height2DComponent
from amulet.chunk.components.biome import Biome2DComponent, Biome3DComponent
from amulet.version import VersionNumber, PlatformVersion

from amulet.utils.world_utils import fast_unique, from_nibble_array

from amulet.level.bedrock._raw import BedrockRawChunk
from amulet.level.bedrock.chunk import BedrockChunk, BedrockChunk0, BedrockChunk29
from amulet.level.bedrock.chunk.components.finalised_state import (
    FinalisedStateComponent,
)

if TYPE_CHECKING:
    from ._level import BedrockRawLevel
    from ._dimension import BedrockRawDimension

log = logging.getLogger(__name__)

SubChunkNDArray = numpy.ndarray
AnyNDArray = numpy.ndarray
T = TypeVar("T")


def cast(obj: Any, cls: type[T]) -> T:
    if not isinstance(obj, cls):
        raise TypeError("obj must be an instance of cls")
    return obj


@cache
def unpack_block_version(block_version: int) -> VersionNumber:
    return VersionNumber(*struct.unpack("4B", struct.pack(">i", block_version)))


def raw_to_native(
    raw_level: BedrockRawLevel,
    dimension: BedrockRawDimension,
    raw_chunk: BedrockRawChunk,
) -> BedrockChunk:
    chunk_data = raw_chunk.chunk_data

    # Get the chunk format version
    chunk_version_byte = chunk_data.pop(b",", None)
    if chunk_version_byte is None:
        chunk_version_byte = chunk_data.pop(b"v", None)
    if chunk_version_byte is None:
        raise RuntimeError
    chunk_version = chunk_version_byte[0]

    # TODO: improve this
    level = raw_level._l
    version = level.translator.get_version(
        "bedrock", tuple(raw_level.version)
    )
    max_version = unpack_block_version(version.data_version)

    # Create the chunk instance
    chunk: BedrockChunk
    if chunk_version >= 29:
        chunk = BedrockChunk29(max_version)
    else:
        chunk = BedrockChunk0(max_version)

    # Parse blocks
    block_component = cast(chunk, BlockComponent)
    if chunk_version >= 3:
        subchunks = {}
        for key in chunk_data.copy().keys():
            if len(key) == 2 and key[0] == 0x2F:
                cy = struct.unpack("b", key[1:2])[0]
                if 25 <= chunk_version <= 28:
                    cy += dimension.bounds().min_y >> 4
                subchunks[cy] = chunk_data.pop(key)
        _load_subchunks(raw_level, subchunks, block_component)
    else:
        section_data = chunk_data.pop(b"\x30", None)
        if section_data is not None:
            block_ids = numpy.frombuffer(
                section_data[: 2**15], dtype=numpy.uint8
            ).astype(numpy.uint16)
            block_data = from_nibble_array(
                numpy.frombuffer(
                    section_data[2**15 : 2**15 + 2**14], dtype=numpy.uint8
                )
            )

            # there is other data here but we are going to skip over it
            combined_palette, block_array = fast_unique(
                numpy.transpose(
                    ((block_ids << 4) + block_data).reshape(16, 16, 128), (0, 2, 1)
                )
            )
            block_component.blocks = {
                i: block_array[:, i * 16 : (i + 1) * 16, :] for i in range(8)
            }
            palette: AnyNDArray = numpy.array(
                [combined_palette >> 4, combined_palette & 15]
            ).T
            chunk_palette = numpy.empty(len(palette), dtype=object)
            for i, b in enumerate(palette):
                chunk_palette[i] = ((None, tuple(b)),)

    # Parse finalised state
    finalised_state_component = cast(chunk, FinalisedStateComponent)
    finalised_state = chunk_data.pop(b"\x36", None)
    if finalised_state is None:
        finalised_state_component.finalised_state = 2
    elif len(finalised_state) == 1:
        # old versions of the game store this as a byte
        finalised_state_component.finalised_state = struct.unpack("b", finalised_state)[
            0
        ]
    elif len(finalised_state) == 4:
        # newer versions store it as an int
        finalised_state_component.finalised_state = struct.unpack(
            "<i", finalised_state
        )[0]

    # Parse biome and height data
    if isinstance(chunk, Biome3DComponent) and b"+" in chunk_data:
        d2d = chunk_data[b"+"]
        cast(chunk, Height2DComponent).height = (
            numpy.frombuffer(d2d[:512], "<i2").reshape((16, 16)).astype(numpy.int64)
        )
        chunk.biomes = _decode_3d_biomes(d2d[512:], dimension.bounds().min_y >> 4)
    elif isinstance(chunk, Biome2DComponent) and b"\x2D" in chunk_data:
        d2d = chunk_data[b"\x2D"]
        cast(chunk, Height2DComponent).height = (
            numpy.frombuffer(d2d[:512], "<i2").reshape((16, 16)).astype(numpy.int64)
        )
        chunk.biomes = (
            numpy.frombuffer(d2d[512:], dtype="uint8")
            .reshape(16, 16)
            .T.astype(numpy.uint32)
        )

    # TODO: implement key support
    # \x33  ticks
    # \x34  block extra data
    # \x35  biome state
    # \x39  7 ints and an end (03)? Honestly don't know what this is
    # \x3A  fire tick?

    # \x2E  2d legacy
    # \x30  legacy terrain

    # Parse block entities
    block_entities = _unpack_nbt_list(chunk_data.pop(b"\x31", b""))
    cast(chunk, BlockEntityComponent).block_entities = _decode_block_entity_list(
        block_entities
    )

    # Parse entities
    entities = _unpack_nbt_list(chunk_data.pop(b"\x32", b""))
    cast(chunk, EntityComponent).entities = _decode_entity_list(
        entities
    ) + _decode_entity_list(raw_chunk.entity_actor)
    raw_chunk.entity_actor.clear()

    return chunk


def _load_subchunks(
    level: BedrockRawLevel, subchunks: dict[int, bytes], chunk: BlockComponent
) -> None:
    """
    Load a list of bytes objects which contain chunk data into the chunk.
    This function should be able to load all sub-chunk formats (technically before it)
    All sub-chunks will almost certainly all have the same sub-chunk version but
    it should be able to handle a case where that is not true.

    The newer formats allow multiple blocks to occupy the same space and the
    newer versions also include a version ber block.
    """
    blocks = chunk.blocks
    block_palette = chunk.block_palette
    block_palette.block_stack_to_index(
        BlockStack(
            Block(
                PlatformVersion("bedrock", VersionNumber(1, 12, 0)),
                namespace="minecraft",
                base_name="air",
                properties={"block_data": IntTag(0)},
            )
        )
    )
    for cy, data in subchunks.items():
        if data[0] in {0, 2, 3, 4, 5, 6, 7}:
            block_ids = numpy.frombuffer(
                data[1 : 1 + 2**12], dtype=numpy.uint8
            ).astype(numpy.uint16)
            block_data = from_nibble_array(
                numpy.frombuffer(
                    data[1 + 2**12 : 1 + 2**12 + 2**11], dtype=numpy.uint8
                )
            )
            numerical_palette, block_array = fast_unique(
                numpy.transpose(
                    ((block_ids << 4) + block_data).reshape(16, 16, 16), (0, 2, 1)
                )
            )
            block_lut: list[int] = []
            for block_id, block_data in numpy.array(
                [numerical_palette >> 4, numerical_palette & 15]
            ).T:
                namespace, base_name = level.legacy_block_map.int_to_str(block_id)
                block_lut.append(
                    block_palette.block_stack_to_index(
                        BlockStack(
                            Block(
                                PlatformVersion("bedrock", VersionNumber(1, 12, 0)),
                                namespace=namespace,
                                base_name=base_name,
                                properties={"block_data": IntTag(block_data)},
                            )
                        )
                    )
                )

            blocks[cy] = numpy.array(block_lut, dtype=numpy.uint32)[block_array]

        else:
            if data[0] == 1:
                storage_count = 1
                data = data[1:]
            elif data[0] == 8:
                storage_count, data = data[1], data[2:]
            elif data[0] == 9:
                # There is an extra byte in this format storing the cy value
                storage_count, cy, data = (
                    data[1],
                    struct.unpack("b", data[2:3])[0],
                    data[3:],
                )
            else:
                raise Exception(f"sub-chunk version {data[0]} is not known.")

            sub_chunk_blocks = numpy.zeros(
                (16, 16, 16, storage_count), dtype=numpy.uint32
            )
            sub_chunk_palette: list[list[Block]] = []
            for storage_index in range(storage_count):
                (
                    sub_chunk_blocks[:, :, :, storage_index],
                    palette_data,
                    data,
                ) = _load_palette_blocks(data)
                palette_data_out: list[Block] = []
                for block_nt in palette_data:
                    block = block_nt.compound
                    *namespace_, base_name = block.get_string("name").py_str.split(
                        ":", 1
                    )
                    namespace = namespace_[0] if namespace_ else "minecraft"

                    properties: PropertyType
                    if "states" in block:
                        properties = {
                            k: v
                            for k, v in block.get_compound("states").items()
                            if isinstance(v, PropertyDataTypes)
                        }
                        version = unpack_block_version(
                            block.get_int("version", IntTag(17694720)).py_int
                        )
                    elif "val" in block:
                        properties = {"block_data": IntTag(block.get_int("val").py_int)}
                        version = VersionNumber(1, 12, 0)
                    else:
                        properties = {}
                        version = unpack_block_version(
                            block.get_int("version", IntTag(17694720)).py_int
                        )

                    palette_data_out.append(
                        Block(
                            PlatformVersion("bedrock", version),
                            namespace=namespace,
                            base_name=base_name,
                            properties=properties,
                        )
                    )
                sub_chunk_palette.append(palette_data_out)

            if storage_count == 1:
                block_lut = [
                    block_palette.block_stack_to_index(BlockStack(block))
                    for block in sub_chunk_palette[0]
                ]
                blocks[cy] = numpy.array(block_lut, dtype=numpy.uint32)[
                    sub_chunk_blocks[:, :, :, 0]
                ]
            elif storage_count > 1:
                # we have two or more storages so need to find the unique block combinations and merge them together
                sub_chunk_palette_, sub_chunk_blocks = numpy.unique(
                    sub_chunk_blocks.reshape(-1, storage_count),
                    return_inverse=True,
                    axis=0,
                )
                block_lut = [
                    block_palette.block_stack_to_index(
                        BlockStack(
                            *(
                                sub_chunk_palette[storage_index][index]
                                for storage_index, index in enumerate(palette_indexes)
                                if storage_index == 0
                                or sub_chunk_palette[storage_index][
                                    index
                                ].namespaced_name
                                != "minecraft:air"
                            )
                        )
                    )
                    for palette_indexes in sub_chunk_palette_
                ]
                blocks[cy] = numpy.array(block_lut, dtype=numpy.uint32)[
                    sub_chunk_blocks.reshape(16, 16, 16)
                ]
            else:
                continue


def _load_palette_blocks(
    data: bytes,
) -> tuple[numpy.ndarray, list[NamedTag], bytes]:
    data, _, blocks = _decode_packed_array(data)
    if blocks is None:
        blocks = numpy.zeros((16, 16, 16), dtype=numpy.int16)
        palette_len = 1
    else:
        palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]

    if palette_len:
        read_context = ReadContext()
        palette = load_nbt_array(
            data,
            compressed=False,
            count=palette_len,
            little_endian=True,
            read_context=read_context,
            string_decoder=utf8_escape_decoder,
        )
        data = data[read_context.offset :]
    else:
        palette = [
            NamedTag(
                CompoundTag(
                    {
                        "name": StringTag("minecraft:air"),
                        "states": CompoundTag(),
                        "version": IntTag(17694723),
                    }
                )
            )
        ]

    return blocks, palette, data


def _decode_3d_biomes(data: bytes, floor_cy: int) -> dict[int, numpy.ndarray]:
    # The 3D biome format consists of 25 16x arrays with the first array corresponding to the lowest sub-chunk in the world
    #  This is -64 in the overworld and 0 in the nether and end
    biomes = {}
    cy = floor_cy
    while data:
        data, bits_per_value, arr = _decode_packed_array(data)
        if bits_per_value == 0:
            value, data = struct.unpack(f"<I", data[:4])[0], data[4:]
            biomes[cy] = numpy.full((16, 16, 16), value, dtype=numpy.uint32)
        elif bits_per_value > 0:
            palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
            biomes[cy] = numpy.frombuffer(data, "<i4", palette_len)[arr].astype(
                numpy.uint32
            )
            data = data[4 * palette_len :]
        cy += 1
    return biomes


def _decode_packed_array(data: bytes) -> tuple[bytes, int, Optional[numpy.ndarray]]:
    """
    Parse a packed array as documented here
    https://gist.github.com/Tomcc/a96af509e275b1af483b25c543cfbf37

    :param data: The data to parse
    :return:
    """
    # Ignore LSB of data (it is a flag) and get compacting level
    bits_per_value, data = struct.unpack("b", data[0:1])[0] >> 1, data[1:]
    if bits_per_value > 0:
        values_per_word = 32 // bits_per_value  # Word = 4 bytes, basis of compacting.
        word_count = -(
            -4096 // values_per_word
        )  # Ceiling divide is inverted floor divide

        arr = numpy.packbits(
            numpy.pad(
                numpy.unpackbits(
                    numpy.frombuffer(
                        bytes(reversed(data[: 4 * word_count])), dtype="uint8"
                    )
                )
                .reshape(-1, 32)[:, -values_per_word * bits_per_value :]
                .reshape(-1, bits_per_value)[-4096:, :],
                [(0, 0), (16 - bits_per_value, 0)],
                "constant",
            )
        ).view(dtype=">i2")[::-1]
        arr = arr.reshape((16, 16, 16)).swapaxes(1, 2)
        data = data[4 * word_count :]
    else:
        arr = None
    return data, bits_per_value, arr


def _unpack_nbt_list(raw_nbt: bytes) -> list[NamedTag]:
    nbt_list = []
    while raw_nbt:
        read_context = ReadContext()
        nbt = load_nbt(
            raw_nbt,
            little_endian=True,
            read_context=read_context,
            string_decoder=utf8_escape_decoder,
        )
        raw_nbt = raw_nbt[read_context.offset :]
        nbt_list.append(nbt)
    return nbt_list


def pop_nbt(tag: CompoundTag, key: str, dtype: type[T]) -> T:
    value = tag.pop(key)
    if not isinstance(value, dtype):
        raise TypeError
    return value


def _decode_block_entity_list(
    block_entities: list[NamedTag],
) -> list[tuple[tuple[int, int, int], BlockEntity]]:
    return [ent for ent in map(_decode_block_entity, block_entities) if ent is not None]


def _decode_block_entity(
    nbt: NamedTag,
) -> Optional[tuple[tuple[int, int, int], BlockEntity]]:
    try:
        tag = nbt.compound
        namespace = ""
        base_name = pop_nbt(tag, "id", StringTag).py_str
        if not base_name:
            raise Exception("entity id is empty")
        x = pop_nbt(tag, "x", IntTag).py_int
        y = pop_nbt(tag, "y", IntTag).py_int
        z = pop_nbt(tag, "z", IntTag).py_int
        return (x, y, z), BlockEntity(
            version=PlatformVersion("bedrock", VersionNumber(1, 0, 0)),
            namespace=namespace,
            base_name=base_name,
            nbt=nbt,
        )
    except Exception as e:
        log.exception(e)
        return None


def _decode_entity_list(entities: list[NamedTag]) -> list[Entity]:
    return [ent for ent in map(_decode_entity, entities) if ent is not None]


def _decode_entity(
    nbt: NamedTag,
) -> Optional[Entity]:
    try:
        tag = nbt.compound
        if "identifier" in tag:
            namespace, base_name = pop_nbt(tag, "identifier", StringTag).py_str.split(
                ":", 1
            )
        elif "id" in tag:
            namespace = ""
            base_name = str(pop_nbt(tag, "id", IntTag).py_int)
        else:
            raise Exception("tag does not have identifier or id keys.")

        pos = pop_nbt(tag, "Pos", ListTag)
        x = pos[0].py_float
        y = pos[1].py_float
        z = pos[2].py_float

        return Entity(
            version=PlatformVersion("bedrock", VersionNumber(1, 0, 0)),
            namespace=namespace,
            base_name=base_name,
            x=x,
            y=y,
            z=z,
            nbt=nbt,
        )
    except Exception as e:
        log.error(e)
        return None

import struct
from typing import Optional, Union, List, Dict, Tuple, TypeVar, Any
import logging

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

from amulet.block import Block
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.chunk.components.block import BlockComponent
from amulet.chunk.components.block_entity import BlockEntityComponent
from amulet.chunk.components.entity import EntityComponent
from amulet.chunk.components.height_2d import Height2DComponent
from amulet.chunk.components.biome import Biome2DComponent, Biome3DComponent

from amulet.utils.world_utils import fast_unique, from_nibble_array

from amulet.level.bedrock._raw import BedrockRawChunk
from amulet.level.bedrock.chunk import BedrockChunk, BedrockChunk0, BedrockChunk29
from amulet.level.bedrock.chunk.components.finalised_state import (
    FinalisedStateComponent,
)
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


def raw_to_native(
    level: BedrockRawLevel,
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

    # Create the chunk instance
    chunk: BedrockChunk
    if chunk_version >= 29:
        chunk = BedrockChunk29(level.max_game_version)
    else:
        chunk = BedrockChunk0(level.max_game_version)

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
        block_component.blocks, chunk_palette = _load_subchunks(subchunks)
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

    if b"+" in chunk_data:
        d2d = chunk_data[b"+"]
        height_component = cast(chunk, Height2DComponent)
        height_component.height = (
            numpy.frombuffer(d2d[:512], "<i2").reshape((16, 16)).astype(numpy.int64)
        )
        biome_component = cast(chunk, Biome3DComponent)
        biome_component.biomes = _decode_3d_biomes(
            d2d[512:], dimension.bounds().min_y >> 4
        )
    elif b"\x2D" in chunk_data:
        d2d = chunk_data[b"\x2D"]
        height_component = cast(chunk, Height2DComponent)
        height_component.height = (
            numpy.frombuffer(d2d[:512], "<i2").reshape((16, 16)).astype(numpy.int64)
        )
        biome_component = cast(chunk, Biome2DComponent)
        biome_component.biome = (
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
    block_entity_component = cast(chunk, BlockEntityComponent)
    block_entities = _unpack_nbt_list(chunk_data.pop(b"\x31", b""))
    block_entity_component.block_entity = _decode_block_entity_list(block_entities)

    # Parse entities
    entity_component = cast(chunk, EntityComponent)
    entities = _unpack_nbt_list(chunk_data.pop(b"\x32", b""))
    entity_component.entities = _decode_entity_list(entities) + _decode_entity_list(
        raw_chunk.entity_actor
    )
    raw_chunk.entity_actor.clear()

    return chunk


def _load_subchunks(
    subchunks: dict[int, Optional[bytes]]
) -> tuple[dict[int, SubChunkNDArray], AnyNDArray]:
    """
    Load a list of bytes objects which contain chunk data
    This function should be able to load all sub-chunk formats (technically before it)
    All sub-chunks will almost certainly all have the same sub-chunk version but
    it should be able to handle a case where that is not true.

    As such this function will return a Chunk and a rather complicated block_palette
    The newer formats allow multiple blocks to occupy the same space and the
    newer versions also include a version ber block. So this will also need
    returning for the translator to handle.

    The block_palette will be a numpy array containing tuple objects
        The tuple represents the "block" however can contain more than one Block object.
        Inside the tuple are one or more tuples.
            These include the block version number and the block itself
                The block version number will be either None if no block version is given
                or a tuple containing 4 ints.

                The block will be either a Block class for the newer formats or a tuple of two ints for the older formats
    """
    blocks: dict[int, SubChunkNDArray] = {}
    palette: list[tuple[tuple[Optional[int], Union[tuple[int, int], Block]], ...]] = [
        (
            (
                17563649,
                Block(
                    namespace="minecraft",
                    base_name="air",
                    properties={"block_data": IntTag(0)},
                ),
            ),
        )
    ]
    for cy, data in subchunks.items():
        if data is None:
            continue
        if data[0] in {0, 2, 3, 4, 5, 6, 7}:
            block_ids = numpy.frombuffer(
                data[1 : 1 + 2**12], dtype=numpy.uint8
            ).astype(numpy.uint16)
            block_data = from_nibble_array(
                numpy.frombuffer(
                    data[1 + 2**12 : 1 + 2**12 + 2**11], dtype=numpy.uint8
                )
            )
            combined_palette, block_array = fast_unique(
                numpy.transpose(
                    ((block_ids << 4) + block_data).reshape(16, 16, 16), (0, 2, 1)
                )
            )
            blocks[cy] = block_array + len(palette)
            for b in numpy.array([combined_palette >> 4, combined_palette & 15]).T:
                palette.append(((None, tuple(b)),))

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
            sub_chunk_palette: list[list[tuple[Optional[int], Block]]] = []
            for storage_index in range(storage_count):
                (
                    sub_chunk_blocks[:, :, :, storage_index],
                    palette_data,
                    data,
                ) = _load_palette_blocks(data)
                palette_data_out: list[tuple[Optional[int], Block]] = []
                for block in palette_data:
                    block = block.compound
                    *namespace_, base_name = block["name"].py_str.split(":", 1)
                    namespace = namespace_[0] if namespace_ else "minecraft"
                    if "version" in block:
                        version: Optional[int] = block.get_int("version").py_int
                    else:
                        version = None

                    if "states" in block or "val" not in block:  # 1.13 format
                        properties = block.get_compound("states", CompoundTag()).py_dict
                        if version is None:
                            version = 17694720  # 1, 14, 0, 0
                    else:
                        properties = {"block_data": IntTag(block["val"].py_int)}
                    palette_data_out.append(
                        (
                            version,
                            Block(
                                namespace=namespace,
                                base_name=base_name,
                                properties=properties,
                            ),
                        )
                    )
                sub_chunk_palette.append(palette_data_out)

            if storage_count == 1:
                blocks[cy] = sub_chunk_blocks[:, :, :, 0] + len(palette)
                palette += [(val,) for val in sub_chunk_palette[0]]
            elif storage_count > 1:
                # we have two or more storages so need to find the unique block combinations and merge them together
                sub_chunk_palette_, sub_chunk_blocks = numpy.unique(
                    sub_chunk_blocks.reshape(-1, storage_count),
                    return_inverse=True,
                    axis=0,
                )
                blocks[cy] = sub_chunk_blocks.reshape(16, 16, 16).astype(
                    numpy.uint32
                ) + len(palette)
                palette += [
                    tuple(
                        sub_chunk_palette[storage_index][index]
                        for storage_index, index in enumerate(palette_indexes)
                        if not (
                            storage_index > 0
                            and sub_chunk_palette[storage_index][index][
                                1
                            ].namespaced_name
                            == "minecraft:air"
                        )
                    )
                    for palette_indexes in sub_chunk_palette_
                ]
            else:
                continue

    # block_palette should now look like this
    # list[
    #   tuple[
    #       tuple[version, Block], ...
    #   ]
    # ]

    numpy_palette, lut = brute_sort_objects(palette)
    for cy in blocks.keys():
        blocks[cy] = lut[blocks[cy]]

    return blocks, numpy_palette


def _load_palette_blocks(
    data: bytes,
) -> Tuple[numpy.ndarray, List[NamedTag], bytes]:
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


def _decode_3d_biomes(data: bytes, floor_cy: int) -> Dict[int, numpy.ndarray]:
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


def _decode_packed_array(data: bytes) -> Tuple[bytes, int, Optional[numpy.ndarray]]:
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


def _unpack_nbt_list(raw_nbt: bytes) -> List[NamedTag]:
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


def _decode_block_entity_list(
    block_entities: List[NamedTag],
) -> List[tuple[tuple[int, int, int], BlockEntity]]:
    return list(filter(bool, map(_decode_block_entity, block_entities)))


def _decode_block_entity(
    nbt: NamedTag,
) -> Optional[tuple[tuple[int, int, int], BlockEntity]]:
    try:
        tag = nbt.compound
        namespace = ""
        base_name = tag.pop("id").py_str
        if not base_name:
            raise Exception("entity id is empty")
        x = tag.pop("x").py_int
        y = tag.pop("y").py_int
        z = tag.pop("z").py_int
        return (x, y, z), BlockEntity(namespace=namespace, base_name=base_name, nbt=nbt)
    except Exception as e:
        log.exception(e)
        return None


def _decode_entity_list(entities: List[NamedTag]) -> List[Entity]:
    return list(filter(bool, map(_decode_entity, entities)))


def _decode_entity(
    nbt: NamedTag,
) -> Optional[Entity]:
    try:
        tag = nbt.compound
        if "identifier" in tag:
            namespace, base_name = tag.pop("identifier").py_str.split(":", 1)
        elif "id" in tag:
            namespace = ""
            base_name = str(tag.pop("id").py_int)
        else:
            raise Exception("tag does not have identifier or id keys.")

        pos: ListTag = tag.pop("Pos")
        x = pos[0].py_float
        y = pos[1].py_float
        z = pos[2].py_float

        return Entity(namespace=namespace, base_name=base_name, x=x, y=y, z=z, nbt=nbt)
    except Exception as e:
        log.error(e)
        return None

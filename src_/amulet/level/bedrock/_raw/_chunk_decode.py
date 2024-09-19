from __future__ import annotations
import struct
from typing import Optional, TypeVar, TYPE_CHECKING, Callable
import logging
from functools import cache

import numpy

from amulet_nbt import (
    CompoundTag,
    IntTag,
    FloatTag,
    StringTag,
    ListTag,
    NamedTag,
    ReadOffset,
    load_array as load_nbt_array,
    read_nbt,
    utf8_escape_encoding,
)

from amulet.block import Block, BlockStack, PropertyValueType
from amulet.block_entity import BlockEntity
from amulet.entity import Entity
from amulet.biome import Biome
from amulet.palette import BlockPalette
from amulet.chunk import ComponentDataMapping
from amulet.chunk.components.sub_chunk_array import SubChunkArrayContainer
from amulet.chunk.components.block import BlockComponent, BlockComponentData
from amulet.chunk.components.block_entity import (
    BlockEntityComponent,
    BlockEntityComponentData,
)
from amulet.chunk.components.entity import EntityComponent, EntityComponentData
from amulet.chunk.components.height_2d import Height2DComponent
from amulet.chunk.components.biome import (
    Biome2DComponent,
    Biome2DComponentData,
    Biome3DComponent,
    Biome3DComponentData,
)
from amulet.game import get_game_version
from amulet.version import VersionNumber, VersionRange

from amulet.utils.world_utils import from_nibble_array
from amulet.utils.numpy import unique_inverse

from amulet.level.bedrock._raw import BedrockRawChunk
from amulet.level.bedrock.chunk import BedrockChunk, BedrockChunk0, BedrockChunk29
from amulet.level.bedrock.chunk.components.finalised_state import (
    FinalisedStateComponent,
)
from amulet.level.bedrock.chunk.components.raw_chunk import RawChunkComponent
from amulet.level.bedrock.chunk.components.chunk_version import ChunkVersionComponent

if TYPE_CHECKING:
    from ._level import BedrockRawLevel
    from ._dimension import BedrockRawDimension

log = logging.getLogger(__name__)

SubChunkNDArray = numpy.ndarray
AnyNDArray = numpy.ndarray
T = TypeVar("T")
GetT = TypeVar("GetT")
SetT = TypeVar("SetT")


@cache
def unpack_block_version(block_version: int) -> VersionNumber:
    return VersionNumber(*struct.unpack("4B", struct.pack(">i", block_version)))


def raw_to_native(
    raw_level: BedrockRawLevel,
    dimension: BedrockRawDimension,
    raw_chunk: BedrockRawChunk,
) -> BedrockChunk:
    game_version = get_game_version("bedrock", raw_level.version)
    max_version = game_version.max_version

    floor_cy = dimension.bounds().min_y >> 4

    chunk_data = raw_chunk.chunk_data

    # Get the chunk format version
    chunk_version_byte = chunk_data.pop(b",", None)
    if chunk_version_byte is None:
        chunk_version_byte = chunk_data.pop(b"v", None)
    if chunk_version_byte is None:
        raise RuntimeError
    chunk_version = chunk_version_byte[0]

    chunk_components: ComponentDataMapping = {}  # type: ignore
    chunk_class: type[BedrockChunk]
    if chunk_version >= 29:
        chunk_class = BedrockChunk29
    else:
        chunk_class = BedrockChunk0

    version_range = VersionRange(
        "bedrock",
        VersionNumber(1, 0, 0),
        max_version,
    )

    chunk_components[RawChunkComponent] = raw_chunk
    chunk_components[ChunkVersionComponent] = chunk_version

    # Parse finalised state
    finalised_state = chunk_data.pop(b"\x36", None)
    if finalised_state is None:
        chunk_components[FinalisedStateComponent] = 2
    elif len(finalised_state) == 1:
        # old versions of the game store this as a byte
        chunk_components[FinalisedStateComponent] = struct.unpack("b", finalised_state)[
            0
        ]
    elif len(finalised_state) == 4:
        # newer versions store it as an int
        chunk_components[FinalisedStateComponent] = struct.unpack(
            "<i", finalised_state
        )[0]

    # Parse blocks
    blocks: list[Block] = []
    for block in dimension.default_block():
        if version_range.contains(block.platform, block.version):
            blocks.append(block)
        else:
            block_ = get_game_version(block.platform, block.version).block.translate(
                "bedrock", max_version, block
            )[0]
            if isinstance(block_, Block):
                blocks.append(block_)
    chunk_components[BlockComponent] = block_component_data = BlockComponentData(
        version_range, (16, 16, 16), BlockStack(*blocks)
    )
    if chunk_version >= 3:
        subchunks = {}
        for key in chunk_data.copy().keys():
            if len(key) == 2 and key[0] == 0x2F:
                cy = struct.unpack("b", key[1:2])[0]
                if 25 <= chunk_version <= 28:
                    cy += floor_cy
                subchunks[cy] = chunk_data.pop(key)
        _load_subchunks(raw_level, subchunks, block_component_data)
    else:
        section_data = chunk_data.pop(b"\x30", None)
        if section_data is not None:
            block_ids = numpy.frombuffer(
                section_data[: 2**15], dtype=numpy.uint8
            ).astype(numpy.uint32)
            block_data = from_nibble_array(
                numpy.frombuffer(section_data[2**15 : 2**15 + 2**14], dtype=numpy.uint8)
            )

            # there is other data here but we are going to skip over it
            combined_palette, block_array = unique_inverse(
                (block_ids << 4) + block_data
            )
            block_array = numpy.transpose(block_array.reshape(16, 16, 128), (0, 2, 1))
            block_component_data.sections = {
                i: block_array[:, i * 16 : (i + 1) * 16, :] for i in range(8)
            }
            palette: AnyNDArray = numpy.array(
                [combined_palette >> 4, combined_palette & 15]
            ).T
            chunk_palette = numpy.empty(len(palette), dtype=object)
            for i, b in enumerate(palette):
                chunk_palette[i] = ((None, tuple(b)),)
            raise NotImplementedError("Need to set up the block palette")

    # Parse block entities
    block_entity_component_data = BlockEntityComponentData(version_range)
    block_entities = _unpack_nbt_list(chunk_data.pop(b"\x31", b""))
    block_entity_component_data.update(_decode_block_entity_list(block_entities))
    chunk_components[BlockEntityComponent] = block_entity_component_data

    # Parse entities
    entity_component_data = EntityComponentData(version_range)
    entities = _unpack_nbt_list(chunk_data.pop(b"\x32", b""))
    entity_component_data |= set(
        _decode_entity_list(entities) + _decode_entity_list(raw_chunk.entity_actor)
    )
    raw_chunk.entity_actor.clear()
    chunk_components[EntityComponent] = entity_component_data

    # Parse biome and height data
    default_biome = dimension.default_biome()
    if not version_range.contains(default_biome.platform, default_biome.version):
        default_biome = get_game_version(
            default_biome.platform, default_biome.version
        ).biome.translate("bedrock", max_version, default_biome)
    if chunk_class.has_component(Biome3DComponent):
        chunk_components[Biome3DComponent] = biome_3d = Biome3DComponentData(
            version_range, (16, 16, 16), default_biome
        )
        if b"+" in chunk_data:
            d2d = chunk_data[b"+"]
            chunk_components[Height2DComponent] = (
                numpy.frombuffer(d2d[:512], "<i2").reshape((16, 16)).astype(numpy.int64)
            )
            _decode_3d_biomes(
                raw_level, biome_3d, d2d[512:], dimension.bounds().min_y >> 4
            )
        else:
            chunk_components[Height2DComponent] = numpy.zeros((16, 16), numpy.int64)
    elif chunk_class.has_component(Biome2DComponent):
        chunk_components[Biome2DComponent] = biome_2d = Biome2DComponentData(
            version_range, (16, 16), default_biome
        )
        if b"\x2D" in chunk_data:
            d2d = chunk_data[b"\x2D"]
            chunk_components[Height2DComponent] = (
                numpy.frombuffer(d2d[:512], "<i2").reshape((16, 16)).astype(numpy.int64)
            )
            _decode_2d_biomes(
                biome_2d,
                raw_level.version,
                numpy.frombuffer(d2d[512:], dtype="uint8"),
                raw_level.biome_id_override.numerical_id_to_namespace_id,
                game_version.biome.numerical_id_to_namespace_id,
            )
        else:
            chunk_components[Height2DComponent] = numpy.zeros((16, 16), numpy.int64)
    else:
        raise RuntimeError

    # TODO: implement key support
    # \x33  ticks
    # \x34  block extra data
    # \x35  biome state
    # \x39  7 ints and an end (03)? Honestly don't know what this is
    # \x3A  fire tick?

    # \x2E  2d legacy
    # \x30  legacy terrain

    return chunk_class.from_component_data(chunk_components)


def _load_palettized_subchunk(
    data: bytes,
    blocks: SubChunkArrayContainer,
    block_palette: BlockPalette,
    storage_count: int,
    cy: int,
) -> None:
    """Load a sub-chunk stored in the palettized format."""
    sub_chunk_blocks = numpy.zeros((16, 16, 16, storage_count), dtype=numpy.uint32)
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
            block_name = block.get_string("name")
            assert block_name is not None
            *namespace_, base_name = block_name.py_str.split(":", 1)
            namespace = namespace_[0] if namespace_ else "minecraft"

            properties: dict[str, PropertyValueType]
            if "states" in block:
                states = block.get_compound("states")
                assert states is not None
                properties = {
                    k: v
                    for k, v in states.items()
                    if isinstance(k, str) and isinstance(v, PropertyValueType)
                }
                version = unpack_block_version(
                    block.get_int("version", IntTag(17694720)).py_int
                )
            elif "val" in block:
                val = block.get_int("val")
                assert val is not None
                properties = {"block_data": IntTag(val.py_int)}
                version = VersionNumber(1, 12)
            else:
                properties = {}
                version = unpack_block_version(
                    block.get_int("version", IntTag(17694720)).py_int
                )

            palette_data_out.append(
                Block(
                    "bedrock",
                    version,
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
                        or sub_chunk_palette[storage_index][index].namespaced_name
                        != "minecraft:air"
                    )
                )
            )
            for palette_indexes in sub_chunk_palette_
        ]
        blocks[cy] = numpy.array(block_lut, dtype=numpy.uint32)[
            sub_chunk_blocks.reshape(16, 16, 16)
        ]


def _load_binary_subchunk(
    data: bytes,
    level: BedrockRawLevel,
    blocks: SubChunkArrayContainer,
    block_palette: BlockPalette,
    cy: int,
) -> None:
    block_ids = numpy.frombuffer(data[: 2**12], dtype=numpy.uint8).astype(numpy.uint32)
    block_data = from_nibble_array(
        numpy.frombuffer(data[2**12 : 2**12 + 2**11], dtype=numpy.uint8)
    )
    numerical_palette, block_array = unique_inverse((block_ids << 4) + block_data)
    block_array = numpy.transpose(block_array.reshape(16, 16, 16), (0, 2, 1))
    block_lut: list[int] = []
    for block_id, block_data in numpy.array(
        [numerical_palette >> 4, numerical_palette & 15]
    ).T:
        try:
            (
                namespace,
                base_name,
            ) = level.block_id_override.numerical_id_to_namespace_id(block_id)
        except KeyError:
            try:
                namespace, base_name = get_game_version(
                    "bedrock", level.version
                ).block.numerical_id_to_namespace_id(block_id)
            except KeyError:
                namespace = "numerical"
                base_name = str(block_id)

        block_lut.append(
            block_palette.block_stack_to_index(
                BlockStack(
                    Block(
                        "bedrock",
                        VersionNumber(1, 12),
                        namespace=namespace,
                        base_name=base_name,
                        properties={"block_data": IntTag(block_data)},
                    )
                )
            )
        )

    blocks[cy] = numpy.array(block_lut, dtype=numpy.uint32)[block_array]


def _load_subchunks(
    level: BedrockRawLevel, subchunks: dict[int, bytes], block_data: BlockComponentData
) -> None:
    """
    Load a list of bytes objects which contain chunk data into the chunk.
    This function should be able to load all sub-chunk formats (technically before it)
    All sub-chunks will almost certainly all have the same sub-chunk version but
    it should be able to handle a case where that is not true.

    The newer formats allow multiple blocks to occupy the same space and the
    newer versions also include a version ber block.
    """
    blocks: SubChunkArrayContainer = block_data.sections
    block_palette: BlockPalette = block_data.palette
    for cy, data in subchunks.items():
        sub_chunk_version, data = data[0], data[1:]

        if sub_chunk_version == 9:
            # There is an extra byte in this format storing the cy value
            storage_count, cy, data = (
                data[0],
                struct.unpack("b", data[1:2])[0],
                data[2:],
            )
            _load_palettized_subchunk(data, blocks, block_palette, storage_count, cy)

        elif sub_chunk_version == 8:
            storage_count, data = data[0], data[1:]
            _load_palettized_subchunk(data, blocks, block_palette, storage_count, cy)

        elif sub_chunk_version == 1:
            _load_palettized_subchunk(data, blocks, block_palette, 1, cy)

        elif 0 <= sub_chunk_version <= 7:
            _load_binary_subchunk(data, level, blocks, block_palette, cy)
        else:
            raise Exception(f"sub-chunk version {sub_chunk_version} is not known.")


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
        read_offset = ReadOffset()
        palette = load_nbt_array(
            data,
            compressed=False,
            count=palette_len,
            little_endian=True,
            read_offset=read_offset,
            string_encoding=utf8_escape_encoding,
        )
        data = data[read_offset.offset :]
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


def _decode_2d_biomes(
    biome_2d_data: Biome2DComponentData,
    version: VersionNumber,
    arr: numpy.ndarray,
    numerical_id_to_namespace_id_override: Callable[[int], tuple[str, str]],
    numerical_id_to_namespace_id: Callable[[int], tuple[str, str]],
) -> None:
    numerical_ids, arr = numpy.unique(arr, return_inverse=True)
    arr = arr.reshape(16, 16).T.astype(numpy.uint32)
    lut = []
    for numerical_id in numerical_ids:
        try:
            (
                namespace,
                base_name,
            ) = numerical_id_to_namespace_id_override(numerical_id)
        except KeyError:
            namespace, base_name = numerical_id_to_namespace_id(numerical_id)
        biome = Biome("bedrock", version, namespace, base_name)
        runtime_id = biome_2d_data.palette.biome_to_index(biome)
        lut.append(runtime_id)
    biome_2d_data.array[:, :] = numpy.array(lut, dtype=numpy.uint32)[arr]


def _decode_3d_biomes(
    raw_level: BedrockRawLevel,
    biome_3d_data: Biome3DComponentData,
    data: bytes,
    floor_cy: int,
) -> None:
    # TODO: how does Bedrock store custom biomes?
    # TODO: can I use one global lookup based on the max version or does it need to be done for the version the chunk was saved in?

    # The 3D biome format consists of 25 16x arrays with the first array corresponding to the lowest sub-chunk in the world
    #  This is -64 in the overworld and 0 in the nether and end
    cy = floor_cy
    game_version = get_game_version("bedrock", raw_level.version)
    while data:
        data, bits_per_value, arr = _decode_packed_array(data)
        if bits_per_value == 0:
            numerical_id = struct.unpack(f"<I", data[:4])[0]
            try:
                (
                    namespace,
                    base_name,
                ) = raw_level.biome_id_override.numerical_id_to_namespace_id(
                    numerical_id
                )
            except KeyError:
                namespace, base_name = game_version.biome.numerical_id_to_namespace_id(
                    numerical_id
                )
            # TODO: should this be based on the chunk version?
            runtime_id = biome_3d_data.palette.biome_to_index(
                Biome("bedrock", raw_level.version, namespace, base_name)
            )
            biome_3d_data.sections[cy] = numpy.full(
                (16, 16, 16), runtime_id, dtype=numpy.uint32
            )
            data = data[4:]
        elif bits_per_value > 0:
            palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
            numerical_palette = numpy.frombuffer(data, "<i4", palette_len)
            lut = []
            for numerical_id in numerical_palette:
                try:
                    (
                        namespace,
                        base_name,
                    ) = raw_level.biome_id_override.numerical_id_to_namespace_id(
                        numerical_id
                    )
                except KeyError:
                    namespace, base_name = (
                        game_version.biome.numerical_id_to_namespace_id(numerical_id)
                    )
                    # TODO: should this be based on the chunk version?
                runtime_id = biome_3d_data.palette.biome_to_index(
                    Biome("bedrock", raw_level.version, namespace, base_name)
                )
                lut.append(runtime_id)
            biome_3d_data.sections[cy] = numpy.array(lut, dtype=numpy.uint32)[arr]
            data = data[4 * palette_len :]
        cy += 1


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
        read_offset = ReadOffset()
        nbt = read_nbt(
            raw_nbt,
            little_endian=True,
            read_offset=read_offset,
            string_encoding=utf8_escape_encoding,
        )
        raw_nbt = raw_nbt[read_offset.offset :]
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
            platform="bedrock",
            version=VersionNumber(1, 0, 0),
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
            # TODO: we should probably look up the real entity id
            namespace = "numerical"
            base_name = str(pop_nbt(tag, "id", IntTag).py_int)
        else:
            raise Exception("tag does not have identifier or id keys.")

        pos = pop_nbt(tag, "Pos", ListTag)
        x, y, z = (v.py_float for v in pos if isinstance(v, FloatTag))

        return Entity(
            platform="bedrock",
            version=VersionNumber(1, 0, 0),
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

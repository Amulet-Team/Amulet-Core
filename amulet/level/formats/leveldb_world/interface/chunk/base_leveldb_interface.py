from __future__ import annotations

from typing import Tuple, Dict, List, Union, Iterable, Optional, TYPE_CHECKING, Any
import struct
import logging

import numpy
from amulet_nbt import (
    ShortTag,
    IntTag,
    StringTag,
    CompoundTag,
    NamedTag,
    load as load_nbt,
    load_many,
    ReadContext,
    utf8_escape_decoder,
    utf8_escape_encoder,
)

import amulet
from amulet.api.block import Block
from amulet.api.chunk import Chunk, StatusFormats

from amulet.utils.numpy_helpers import brute_sort_objects
from amulet.utils.world_utils import fast_unique, from_nibble_array
from amulet.api.wrapper import Interface
from amulet.api.data_types import (
    AnyNDArray,
    SubChunkNDArray,
    PlatformType,
    VersionNumberTuple,
    VersionIdentifierTuple,
)
from amulet.level import loader
from amulet.api.wrapper import EntityIDType, EntityCoordType
from .leveldb_chunk_versions import chunk_to_game_version
from amulet.api.chunk.entity_list import EntityList
from amulet.level.formats.leveldb_world.chunk import ChunkData

if TYPE_CHECKING:
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity
    from amulet.api.chunk.blocks import Blocks
    from amulet.api.wrapper import Translator

log = logging.getLogger(__name__)

# This is here to scale a 4x array to a 16x array. This can be removed when we natively support 16x array
_scale_grid = tuple(numpy.meshgrid(*[numpy.arange(16) // 4] * 3, indexing="ij"))


class BaseLevelDBInterface(Interface):

    chunk_version: int = None

    def __init__(self):
        self._feature_options = {
            "finalised_state": ["int0-2"],
            "data_2d": ["height512|biome256", "height512|biome4096"],
            "block_entities": ["31list"],
            "block_entity_format": [EntityIDType.namespace_str_id, EntityIDType.str_id],
            "block_entity_coord_format": [EntityCoordType.xyz_int],
            "entities": ["32list", "actor"],
            "entity_format": [
                EntityIDType.namespace_str_identifier,
                EntityIDType.int_id,
            ],
            "entity_coord_format": [EntityCoordType.Pos_list_float],
            "terrain": ["30array", "2farray", "2f1palette", "2fnpalette"],
        }
        self._features = {key: None for key in self._feature_options.keys()}

    def _set_feature(self, feature: str, option: Any):
        assert feature in self._feature_options, f"{feature} is not a valid feature."
        assert (
            option in self._feature_options[feature]
        ), f'Invalid option {option} for feature "{feature}"'
        self._features[feature] = option

    def is_valid(self, key: Tuple) -> bool:
        return key[0] == "bedrock" and key[1] == self.chunk_version

    def get_translator(
        self,
        max_world_version: Tuple[PlatformType, VersionNumberTuple],
        data: ChunkData = None,
    ) -> Tuple["Translator", VersionNumberTuple]:
        """
        Get the Translator class for the requested version.
        :param max_world_version: The game version the world was last opened in. Version number tuple or data version number.
        :param data: Optional data to get translator based on chunk version rather than world version
        :return: Tuple[Translator, version number for PyMCTranslate to use]
        """
        if data:
            if b"," in data:
                chunk_version = data[b","][0]
            else:
                chunk_version = data[b"v"][0]
            game_version = chunk_to_game_version(max_world_version[1], chunk_version)
        else:
            game_version = max_world_version[1]
        return loader.Translators.get(("bedrock", game_version)), game_version

    @staticmethod
    def _chunk_key_to_sub_chunk(cy: int, min_y: int) -> int:
        """Convert the database sub-chunk key to the sub-chunk index."""
        return cy

    @staticmethod
    def _get_sub_chunk_storage_byte(cy: int, min_y: int) -> bytes:
        return struct.pack("b", cy)

    def decode(
        self, cx: int, cz: int, chunk_data: ChunkData, bounds: Tuple[int, int]
    ) -> Tuple[Chunk, AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data given by the format
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param chunk_data: Raw chunk data provided by the format.
        :param bounds: The minimum and maximum height of the chunk.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
        chunk = Chunk(cx, cz)
        chunk_palette = numpy.empty(0, dtype=object)
        chunk.misc = {"bedrock_chunk_data": chunk_data}

        chunk_data.pop(b"v", None)
        chunk_data.pop(b",", None)

        if self._features["terrain"].startswith(
            "2f"
        ):  # ["2farray", "2f1palette", "2fnpalette"]
            subchunks = {}
            for key in chunk_data.copy().keys():
                if len(key) == 2 and key[0:1] == b"\x2F":
                    cy = struct.unpack("b", key[1:2])[0]
                    subchunks[
                        self._chunk_key_to_sub_chunk(cy, bounds[0] >> 4)
                    ] = chunk_data.pop(key)
            chunk.blocks, chunk_palette = self._load_subchunks(subchunks)
        elif self._features["terrain"] == "30array":
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
                chunk.blocks = {
                    i: block_array[:, i * 16 : (i + 1) * 16, :] for i in range(8)
                }
                palette: AnyNDArray = numpy.array(
                    [combined_palette >> 4, combined_palette & 15]
                ).T
                chunk_palette = numpy.empty(len(palette), dtype=object)
                for i, b in enumerate(palette):
                    chunk_palette[i] = ((None, tuple(b)),)

        else:
            raise Exception

        if self._features["finalised_state"] == "int0-2":
            state = chunk_data.pop(b"\x36", None)
            val = 2
            if isinstance(state, bytes):
                if len(state) == 1:
                    # old versions of the game store this as a byte
                    val = struct.unpack("b", state)[0]
                elif len(state) == 4:
                    # newer versions store it as an int
                    val = struct.unpack("<i", state)[0]
            chunk.status = val

        if b"+" in chunk_data:
            height, biome = self._decode_height_3d_biomes(
                chunk_data[b"+"], bounds[0] >> 4
            )
            chunk.misc["height"] = height
            chunk.biomes = biome
        elif b"\x2D" in chunk_data:
            d2d = chunk_data[b"\x2D"]
            height, biome = (
                numpy.frombuffer(d2d[:512], "<i2").reshape((16, 16)),
                d2d[512:],
            )
            chunk.misc["height"] = height
            chunk.biomes = numpy.frombuffer(biome, dtype="uint8").reshape(16, 16).T

        # TODO: implement key support
        # \x2D  heightmap and biomes
        # \x31  block entity
        # \x32  entity
        # \x33  ticks
        # \x34  block extra data
        # \x35  biome state
        # \x39  7 ints and an end (03)? Honestly don't know what this is
        # \x3A  fire tick?

        # \x2E  2d legacy
        # \x30  legacy terrain

        # unpack block entities and entities
        if self._features["block_entities"] == "31list":
            block_entities = self._unpack_nbt_list(chunk_data.pop(b"\x31", b""))
            chunk.block_entities = self._decode_block_entity_list(block_entities)

        if self._features["entities"] in ("32list", "actor"):
            entities = self._unpack_nbt_list(chunk_data.pop(b"\x32", b""))
            if amulet.entity_support:
                chunk.entities = self._decode_entity_list(entities)
            else:
                chunk._native_entities = EntityList(self._decode_entity_list(entities))
                chunk._native_version = (
                    "bedrock",
                    (0, 0, 0),
                )  # TODO: find a way to determine entity version

        if self._features["entities"] == "actor":
            if chunk_data.entity_actor:
                if amulet.entity_support:
                    chunk.entities += self._decode_entity_list(chunk_data.entity_actor)
                else:
                    chunk._native_entities += self._decode_entity_list(
                        chunk_data.entity_actor
                    )
                    chunk._native_version = ("bedrock", (0, 0, 0))
                chunk_data.entity_actor.clear()

        return chunk, chunk_palette

    def encode(
        self,
        chunk: Chunk,
        palette: AnyNDArray,
        max_world_version: VersionIdentifierTuple,
        bounds: Tuple[int, int],
    ) -> Dict[bytes, Optional[bytes]]:
        chunk_data = chunk.misc.get("bedrock_chunk_data", {})
        if isinstance(chunk_data, ChunkData):
            pass
        elif isinstance(chunk_data, dict):
            chunk_data = ChunkData(
                {
                    k: v
                    for k, v in chunk_data.items()
                    if isinstance(k, bytes) and isinstance(v, bytes)
                }
            )
        else:
            chunk_data = ChunkData()

        chunk_data: ChunkData

        # chunk version
        if self.chunk_version is not None:
            chunk_data[b"v" if self.chunk_version <= 20 else b","] = bytes(
                [self.chunk_version]
            )

        # terrain data
        terrain = self._encode_subchunks(
            chunk.blocks, palette, bounds, max_world_version
        )
        min_y = bounds[0] // 16
        for cy, sub_chunk in terrain.items():
            chunk_data[
                b"\x2F" + self._get_sub_chunk_storage_byte(cy, min_y)
            ] = sub_chunk

        # chunk status
        if self._features["finalised_state"] == "int0-2":
            chunk_data[b"\x36"] = struct.pack(
                "<i", chunk.status.as_type(StatusFormats.Bedrock)
            )

        # biome and height data
        if self._features["data_2d"] == "height512|biome256":
            d2d: List[bytes] = [self._encode_height(chunk)]
            chunk.biomes.convert_to_2d()
            d2d.append(chunk.biomes.astype("uint8").T.tobytes())
            chunk_data[b"\x2D"] = b"".join(d2d)
            if b"+" in chunk_data:
                chunk_data[b"+"] = None
        elif self._features["data_2d"] == "height512|biome4096":
            chunk_data[b"+"] = self._encode_height_3d_biomes(
                chunk, bounds[0] >> 4, bounds[1] >> 4
            )
            if b"\x2D" in chunk_data:
                chunk_data[b"\x2D"] = None

        # pack block entities and entities
        if self._features["block_entities"] == "31list":
            block_entities_out = self._encode_block_entity_list(chunk.block_entities)

            if block_entities_out:
                chunk_data[b"\x31"] = self._pack_nbt_list(block_entities_out)
            else:
                chunk_data[b"\x31"] = None

        if self._features["entities"] == "32list":

            def save_entities(entities_out):
                if entities_out:
                    chunk_data[b"\x32"] = self._pack_nbt_list(entities_out)
                else:
                    chunk_data[b"\x32"] = None

            if amulet.entity_support:
                save_entities(self._encode_entity_list(chunk.entities))
            else:
                try:
                    if chunk._native_version[0] == "bedrock":
                        save_entities(self._encode_entity_list(chunk._native_entities))
                except:
                    pass

        elif self._features["entities"] == "actor":
            chunk_data.entity_actor.clear()
            if amulet.entity_support:
                chunk_data.entity_actor.extend(self._encode_entity_list(chunk.entities))
            else:
                try:
                    if chunk._native_version[0] == "bedrock":
                        chunk_data.entity_actor.extend(
                            self._encode_entity_list(chunk._native_entities)
                        )
                except:
                    pass

        return chunk_data

    def _load_subchunks(
        self, subchunks: Dict[int, Optional[bytes]]
    ) -> Tuple[Dict[int, SubChunkNDArray], AnyNDArray]:
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
        blocks: Dict[int, SubChunkNDArray] = {}
        palette: List[
            Tuple[Tuple[Optional[int], Union[Tuple[int, int], Block]], ...]
        ] = [
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
                sub_chunk_palette: List[List[Tuple[Optional[int], Block]]] = []
                for storage_index in range(storage_count):
                    (
                        sub_chunk_blocks[:, :, :, storage_index],
                        palette_data,
                        data,
                    ) = self._load_palette_blocks(data)
                    palette_data_out: List[Tuple[Optional[int], Block]] = []
                    for block in palette_data:
                        block = block.compound
                        namespace, base_name = block["name"].py_str.split(":", 1)
                        if "version" in block:
                            version: Optional[int] = block.get_int("version").py_int
                        else:
                            version = None

                        if "states" in block:  # 1.13 format
                            properties = block.get_compound("states").py_dict
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
        # List[
        #   Tuple[
        #       Tuple[version, Block], ...
        #   ]
        # ]

        numpy_palette, lut = brute_sort_objects(palette)
        for cy in blocks.keys():
            blocks[cy] = lut[blocks[cy]]

        return blocks, numpy_palette

    def _encode_subchunks(
        self,
        blocks: "Blocks",
        palette: AnyNDArray,
        bounds: Tuple[int, int],
        max_world_version: VersionIdentifierTuple,
    ) -> Dict[int, Optional[bytes]]:
        raise NotImplementedError

    def _save_subchunks_1(
        self, blocks: "Blocks", palette: AnyNDArray
    ) -> Dict[int, Optional[bytes]]:
        for index, block in enumerate(palette):
            block: Tuple[Tuple[None, Block], ...]
            block_data_tag = block[0][1].properties.get("block_data", IntTag(0))
            if isinstance(block_data_tag, IntTag):
                block_data = block_data_tag.py_int
                # if block_data >= 16:
                #     block_data = 0
            else:
                block_data = 0

            palette[index] = NamedTag(
                CompoundTag(
                    {
                        "name": StringTag(block[0][1].namespaced_name),
                        "val": ShortTag(block_data),
                    }
                )
            )
        chunk = {}
        for cy in range(16):
            if cy in blocks:
                palette_index, sub_chunk = fast_unique(blocks.get_sub_chunk(cy))
                sub_chunk_palette = list(palette[palette_index])
                chunk[cy] = b"\x01" + self._save_palette_subchunk(
                    sub_chunk.ravel(), sub_chunk_palette
                )
            else:
                chunk[cy] = None
        return chunk

    # These arent actual blocks, just ids pointing to the block_palette.

    @staticmethod
    def _decode_packed_array(data: bytes) -> Tuple[bytes, int, Optional[numpy.ndarray]]:
        """
        Parse a packed array as documented here
        https://gist.github.com/Tomcc/a96af509e275b1af483b25c543cfbf37

        :param data: The data to parse
        :return:
        """
        # Ignore LSB of data (its a flag) and get compacting level
        bits_per_value, data = struct.unpack("b", data[0:1])[0] >> 1, data[1:]
        if bits_per_value > 0:
            values_per_word = (
                32 // bits_per_value
            )  # Word = 4 bytes, basis of compacting.
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

    def _decode_height_3d_biomes(
        self, data: bytes, floor_cy: int
    ) -> Tuple[numpy.ndarray, Dict[int, numpy.ndarray]]:
        # The 3D biome format consists of 25 16x arrays with the first array corresponding to the lowest sub-chunk in the world
        #  This is -64 in the overworld and 0 in the nether and end
        # TODO: make this support the full 16x
        heightmap, data = (
            numpy.frombuffer(data[:512], "<i2").reshape((16, 16)),
            data[512:],
        )
        biomes = {}
        cy = floor_cy
        while data:
            data, bits_per_value, arr = self._decode_packed_array(data)
            if bits_per_value == 0:
                value, data = struct.unpack(f"<I", data[:4])[0], data[4:]
                # TODO: when the new biome system supports ints just return the value
                biomes[cy] = numpy.full((4, 4, 4), value, dtype=numpy.uint32)
            elif bits_per_value > 0:
                arr = arr[::4, ::4, ::4]
                palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
                biomes[cy] = numpy.frombuffer(data, "<i4", palette_len)[arr].astype(
                    numpy.uint32
                )
                data = data[4 * palette_len :]
            cy += 1
        return heightmap, biomes

    def _encode_height(self, chunk) -> bytes:
        height = chunk.misc.get("height")
        if isinstance(height, numpy.ndarray) and height.size == 256:
            return height.ravel().astype("<i2").tobytes()
        else:
            return b"\x00" * 512

    def _encode_height_3d_biomes(
        self, chunk: Chunk, floor_cy: int, ceil_cy: int
    ) -> bytes:
        d2d: List[bytes] = [self._encode_height(chunk)]
        chunk.biomes.convert_to_3d()
        # at least one biome array needs to be defined
        # all biome arrays below the highest biome array must be populated.
        highest = next(
            (cy for cy in range(ceil_cy, floor_cy - 1, -1) if cy in chunk.biomes), None
        )
        if highest is None:
            # populate lowest array
            chunk.biomes.create_section(floor_cy)
        else:
            for cy in range(highest - 1, floor_cy - 1, -1):
                if cy not in chunk.biomes:
                    chunk.biomes.add_section(
                        cy,
                        numpy.repeat(
                            # get the array for the sub-chunk above and get the lowest slice
                            chunk.biomes.get_section(cy + 1)[:, :1, :],
                            4,  # Repeat this slice 4 times in the first axis
                            1,  # TODO: When biome editing supports 16x this will need to be changed.
                        ),
                    )

        for cy in range(floor_cy, floor_cy + 25):
            if cy in chunk.biomes:
                arr = chunk.biomes.get_section(cy)
                palette, arr_uniq = numpy.unique(arr, return_inverse=True)
                if len(palette) == 1:
                    d2d.append(b"\x01")
                else:
                    d2d.append(
                        self._encode_packed_array(
                            arr_uniq.reshape(arr.shape)[_scale_grid]
                        )
                    )
                    d2d.append(struct.pack("<I", len(palette)))
                d2d.append(palette.astype("<i4").tobytes())
            else:
                d2d.append(b"\xFF")

        return b"".join(d2d)

    def _load_palette_blocks(
        self,
        data: bytes,
    ) -> Tuple[numpy.ndarray, List[NamedTag], bytes]:
        data, _, blocks = self._decode_packed_array(data)
        if blocks is None:
            blocks = numpy.zeros((16, 16, 16), dtype=numpy.int16)
            palette_len = 1
        else:
            palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]

        if palette_len:
            read_context = ReadContext()
            palette = load_many(
                data,
                compressed=False,
                count=palette_len,
                little_endian=True,
                read_context=read_context,
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

    @staticmethod
    def _encode_packed_array(arr: numpy.ndarray, min_bit_size=1) -> bytes:
        bits_per_value = max(int(numpy.amax(arr)).bit_length(), min_bit_size)
        if bits_per_value == 7:
            bits_per_value = 8
        elif 9 <= bits_per_value <= 15:
            bits_per_value = 16
        header = bytes([bits_per_value << 1])

        values_per_word = 32 // bits_per_value  # Word = 4 bytes, basis of compacting.
        word_count = -(
            -4096 // values_per_word
        )  # Ceiling divide is inverted floor divide

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

    def _save_palette_subchunk(
        self, blocks: numpy.ndarray, palette: List[NamedTag]
    ) -> bytes:
        """Save a single layer of blocks in the block_palette format"""
        return b"".join(
            [self._encode_packed_array(blocks), struct.pack("<I", len(palette))]
            + [
                block.save_to(
                    compressed=False,
                    little_endian=True,
                    string_encoder=utf8_escape_encoder,
                )
                for block in palette
            ]
        )

    @staticmethod
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

    @staticmethod
    def _pack_nbt_list(nbt_list: List[NamedTag]):
        return b"".join(
            [
                nbt.save_to(
                    compressed=False,
                    little_endian=True,
                    string_encoder=utf8_escape_encoder,
                )
                for nbt in nbt_list
                if isinstance(nbt, NamedTag)
            ]
        )

    def _decode_entity_list(self, entities: List[NamedTag]) -> List["Entity"]:
        entities_out = []
        for nbt in entities:
            entity = self._decode_entity(
                nbt,
                self._features["entity_format"],
                self._features["entity_coord_format"],
            )
            if entity is not None:
                entities_out.append(entity)

        return entities_out

    def _encode_entity_list(self, entities: "EntityList") -> List[NamedTag]:
        entities_out = []
        for entity in entities:
            nbt = self._encode_entity(
                entity,
                self._features["entity_format"],
                self._features["entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt)

        return entities_out

    def _decode_block_entity_list(
        self, block_entities: List[NamedTag]
    ) -> List["BlockEntity"]:
        entities_out = []
        for nbt in block_entities:
            entity = self._decode_block_entity(
                nbt,
                self._features["block_entity_format"],
                self._features["block_entity_coord_format"],
            )
            if entity is not None:
                entities_out.append(entity)

        return entities_out

    def _encode_block_entity_list(
        self, block_entities: Iterable["BlockEntity"]
    ) -> List[NamedTag]:
        entities_out = []
        for entity in block_entities:
            nbt = self._encode_block_entity(
                entity,
                self._features["block_entity_format"],
                self._features["block_entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt)

        return entities_out

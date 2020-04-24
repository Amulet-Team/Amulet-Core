from __future__ import annotations

from typing import Tuple, Dict, List, Union, Iterable, Optional

import struct
import numpy
import amulet_nbt

import amulet
from amulet.api.block import Block
from amulet.api.block_entity import BlockEntity
from amulet.api.entity import Entity
from amulet.api.chunk import Chunk
from amulet.api.chunk.blocks import Blocks
from amulet.api.chunk.entity_list import EntityList
from amulet.utils.world_utils import fast_unique
from amulet.world_interface.chunk.interfaces import Interface
from amulet.world_interface.chunk import translators
from amulet.world_interface.chunk.interfaces.leveldb.leveldb_chunk_versions import (
    chunk_to_game_version,
)


def brute_sort_objects(data) -> Tuple[numpy.ndarray, numpy.ndarray]:
    indexes = {}
    unique = []
    inverse = []
    index = 0
    for d in data:
        if d not in indexes:
            indexes[d] = index
            index += 1
            unique.append(d)
        inverse.append(indexes[d])

    unique_ = numpy.empty(len(unique), dtype=object)
    for index, obj in enumerate(unique):
        unique_[index] = obj

    return unique_, numpy.array(inverse)


def brute_sort_objects_no_hash(data) -> Tuple[numpy.ndarray, numpy.ndarray]:
    unique = []
    inverse = numpy.zeros(dtype=numpy.uint, shape=len(data))
    for i, d in enumerate(data):
        try:
            index = unique.index(d)
        except ValueError:
            index = len(unique)
            unique.append(d)
        inverse[i] = index

    unique_ = numpy.empty(len(unique), dtype=object)
    for index, obj in enumerate(unique):
        unique_[index] = obj

    return unique_, numpy.array(inverse)


class BaseLevelDBInterface(Interface):
    def __init__(self):
        feature_options = {
            "chunk_version": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "finalised_state": ["int0-2"],
            "data_2d": ["height512|biome256", "unused_height512|biome256"],
            "block_entities": ["31list"],
            "block_entity_format": ["namespace-str-id", "str-id"],
            "block_entity_coord_format": ["xyz-int"],
            "entities": ["32list"],
            "entity_format": ["namespace-str-identifier", "int-id"],
            "entity_coord_format": ["Pos-list-float"],
            "terrain": ["2farray", "2f1palette", "2fnpalette"],
        }
        self.features = {key: None for key in feature_options.keys()}

    def is_valid(self, key: Tuple) -> bool:
        return key[0] == "bedrock" and self.features["chunk_version"] == key[1]

    def get_translator(
        self,
        max_world_version: Tuple[str, Tuple[int, int, int]],
        data: Dict[bytes, bytes] = None,
    ) -> Tuple[translators.Translator, Tuple[int, int, int]]:
        """
        Get the Translator class for the requested version.
        :param max_world_version: The game version the world was last opened in.
        :type max_world_version: Java: int (DataVersion)    Bedrock: Tuple[int, int, int, ...] (game version number)
        :param data: Optional data to get translator based on chunk version rather than world version
        :param data: Any
        :return: Tuple[Translator, version number for PyMCTranslate to use]
        :rtype: Tuple[translators.Translator, Tuple[int, int, int]]
        """
        if data:
            chunk_version = data[b"v"][0]
            game_version = chunk_to_game_version(max_world_version[1], chunk_version)
        else:
            game_version = max_world_version[1]
        return translators.loader.get(("bedrock", game_version)), game_version

    def decode(
        self, cx: int, cz: int, data: Dict[bytes, bytes]
    ) -> Tuple[Chunk, numpy.ndarray]:
        # chunk_key_base = struct.pack("<ii", cx, cz)

        chunk = Chunk(cx, cz)

        if self.features["terrain"] in ["2farray", "2f1palette", "2fnpalette"]:
            subchunks = [data.get(b"\x2F" + bytes([i]), None) for i in range(16)]
            chunk.blocks, palette = self._load_subchunks(subchunks)
        else:
            raise Exception

        if self.features["finalised_state"] == "int0-2":
            if b"\x36" in data:
                val = struct.unpack("<i", data[b"\x36"])[0]
            else:
                val = 2
            chunk.status = val

        if self.features["data_2d"] in [
            "height512|biome256",
            "unused_height512|biome256",
        ]:
            d2d = data.get(b"\x2D", b"\x00" * 768)
            height, biome = d2d[:512], d2d[512:]
            if self.features["data_2d"] == "height512|biome256":
                pass  # TODO: put this data somewhere
            chunk.biomes = numpy.frombuffer(biome, dtype="uint8")

        # TODO: impliment key support
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
        if self.features["block_entities"] == "31list":
            block_entities = self._unpack_nbt_list(data.get(b"\x31", b""))
            chunk.block_entities = self._decode_block_entities(block_entities)

        if self.features["entities"] == "32list" and amulet.entity_support:
            entities = self._unpack_nbt_list(data.get(b"\x32", b""))
            chunk.entities = self._decode_entities(entities)

        return chunk, palette

    def encode(
        self,
        chunk: Chunk,
        palette: numpy.ndarray,
        max_world_version: Tuple[int, int, int],
    ) -> Dict[bytes, bytes]:
        chunk_data = {}

        # chunk version
        if self.features["chunk_version"] is not None:
            chunk_data[b"v"] = bytes([self.features["chunk_version"]])

        # terrain data
        if self.features["terrain"] == "2farray":
            terrain = self._save_subchunks_0(chunk.blocks, palette)
        elif self.features["terrain"] == "2f1palette":
            terrain = self._save_subchunks_1(chunk.blocks, palette)
        elif self.features["terrain"] == "2fnpalette":
            terrain = self._save_subchunks_8(chunk.blocks, palette)
        else:
            raise Exception

        for y, sub_chunk in enumerate(terrain):
            chunk_data[b"\x2F" + bytes([y])] = sub_chunk

        # chunk status
        if self.features["finalised_state"] == "int0-2":
            chunk_data[b"\x36"] = struct.pack("<i", chunk.status.as_type("b"))

        # biome and height data
        if self.features["data_2d"] in [
            "height512|biome256",
            "unused_height512|biome256",
        ]:
            if self.features["data_2d"] == "height512|biome256":
                d2d = b"\x00" * 512  # TODO: get this data from somewhere
            else:
                d2d = b"\x00" * 512
            d2d += chunk.biomes.convert_to_format(256).astype("uint8").tobytes()
            chunk_data[b"\x2D"] = d2d

        # pack block entities and entities
        if self.features["block_entities"] == "31list":
            block_entities_out = self._encode_block_entities(chunk.block_entities)

            if block_entities_out:
                chunk_data[b"\x31"] = self._pack_nbt_list(block_entities_out)
            else:
                chunk_data[b"\x31"] = None

        if self.features["entities"] == "32list":
            if amulet.entity_support:
                entities_out = self._encode_entities(chunk.entities)
            else:
                entities_out = ""

            if entities_out:
                chunk_data[b"\x32"] = self._pack_nbt_list(entities_out)
            else:
                chunk_data[b"\x32"] = None

        return chunk_data

    def _load_subchunks(
        self, subchunks: List[None, bytes]
    ) -> Tuple[Dict[int, numpy.ndarray], numpy.ndarray]:
        """
        Load a list of bytes objects which contain chunk data
        This function should be able to load all sub-chunk formats (technically before it)
        All sub-chunks will almost certainly all have the same sub-chunk version but
        it should be able to handle a case where that is not true.

        As such this function will return a Chunk and a rather complicated palette
        The newer formats allow multiple blocks to occupy the same space and the
        newer versions also include a version ber block. So this will also need
        returning for the translator to handle.

        The palette will be a numpy array containing tuple objects
            The tuple represents the "block" however can contain more than one Block object.
            Inside the tuple are one or more tuples.
                These include the block version number and the block itself
                    The block version number will be either None if no block version is given
                    or a tuple containing 4 ints.

                    The block will be either a Block class for the newer formats or a tuple of two ints for the older formats
        """
        blocks: Dict[int, numpy.ndarray] = {}
        palette: List[
            Tuple[
                Tuple[
                    Optional[Tuple[int, int, int, int]],
                    Union[Tuple[int, int], Block],
                ]
            ]
        ] = [
            (
                (
                    (1, 7, 0, 0),
                    Block(
                        namespace="minecraft",
                        base_name="air",
                        properties={"block_data": amulet_nbt.TAG_Int(0)},
                    ),
                ),
            )
        ]
        for cy, data in enumerate(subchunks):
            if data is None:
                continue

            if data[0] in [0, 2, 3, 4, 5, 6, 7]:
                raise NotImplementedError(
                    "The old Bedrock numerical chunk format is not currently implemented"
                )

            elif data[0] in [1, 8]:
                if data[0] == 1:
                    storage_count = 1
                    data = data[1:]
                else:
                    storage_count, data = data[1], data[2:]

                sub_chunk_blocks = numpy.zeros(
                    (16, 16, 16, storage_count), dtype=numpy.uint32
                )
                sub_chunk_palette: List[
                    List[Tuple[Optional[Tuple[int, int, int, int]], Block]]
                ] = []
                for storage_index in range(storage_count):
                    (
                        sub_chunk_blocks[:, :, :, storage_index],
                        palette_data,
                        data,
                    ) = self._load_palette_blocks(data)
                    palette_data_out: List[
                        Tuple[Optional[Tuple[int, int, int, int]], Block]
                    ] = []
                    for block in palette_data:
                        namespace, base_name = block["name"].value.split(":", 1)
                        if "version" in block:
                            version = tuple(
                                numpy.array([block["version"].value], dtype=">u4").view(
                                    numpy.uint8
                                )
                            )
                        else:
                            version = None

                        if "states" in block:  # 1.13 format
                            properties = block["states"].value
                            if version is None:
                                version = (1, 14, 0, 0)
                        else:
                            properties = {
                                "block_data": amulet_nbt.TAG_Int(block["val"].value)
                            }
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
                    blocks[cy] = sub_chunk_blocks[:, :, :, 0] + len(
                        palette
                    )
                    palette += [(val,) for val in sub_chunk_palette[0]]
                elif storage_count > 1:
                    # we have two or more storages so need to find the unique block combinations and merge them together
                    sub_chunk_palette_, sub_chunk_blocks = numpy.unique(
                        sub_chunk_blocks.reshape(-1, storage_count),
                        return_inverse=True,
                        axis=0,
                    )
                    blocks[cy] = sub_chunk_blocks.reshape(
                        16, 16, 16
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
                    raise Exception("Is a chunk with no storages allowed?")

        # palette should now look like this
        # List[
        #   Tuple[
        #       Tuple[version, Block], ...
        #   ]
        # ]

        numpy_palette, lut = brute_sort_objects(palette)
        for cy in blocks.keys():
            blocks[cy] = lut[blocks[cy]]

        return blocks, numpy_palette

    def _save_subchunks_0(
        self, blocks: Blocks, palette: numpy.ndarray
    ) -> List[Optional[bytes]]:
        raise NotImplementedError

    def _save_subchunks_1(
        self, blocks: Blocks, palette: numpy.ndarray
    ) -> List[Optional[bytes]]:
        for index, block in enumerate(palette):
            block: Tuple[Tuple[None, Block], ...]
            block_data = block[0][1].properties.get("block_data", amulet_nbt.TAG_Int(0))
            if isinstance(block_data, amulet_nbt.TAG_Int):
                block_data = block_data.value
                if block_data >= 16:
                    block_data = 0
            else:
                block_data = 0

            palette[index] = amulet_nbt.NBTFile(
                amulet_nbt.TAG_Compound(
                    {
                        "name": amulet_nbt.TAG_String(block[0][1].namespaced_name),
                        "val": amulet_nbt.TAG_Short(block_data),
                    }
                )
            )
        chunk = []
        for cy in range(16):
            if cy in blocks:
                palette_index, sub_chunk = fast_unique(blocks.get_sub_chunk(cy))
                sub_chunk_palette = list(palette[palette_index])
                chunk.append(
                    b"\x01"
                    + self._save_palette_subchunk(sub_chunk.ravel(), sub_chunk_palette)
                )
        return chunk

    def _save_subchunks_8(
        self, blocks: Blocks, palette: numpy.ndarray
    ) -> List[Optional[bytes]]:
        palette_depth = numpy.array([len(block) for block in palette])
        if palette.size:
            if palette[0][0][0] is None:
                air = amulet_nbt.NBTFile(
                    amulet_nbt.TAG_Compound(
                        {
                            "name": amulet_nbt.TAG_String("minecraft:air"),
                            "val": amulet_nbt.TAG_Short(0),
                        }
                    )
                )
            else:
                air = amulet_nbt.NBTFile(
                    amulet_nbt.TAG_Compound(
                        {
                            "name": amulet_nbt.TAG_String("minecraft:air"),
                            "states": amulet_nbt.TAG_Compound({}),
                            "version": amulet_nbt.TAG_Int(17_629_184),
                        }
                    )
                )

            for index, block in enumerate(palette):
                block: Tuple[Tuple[Union[Tuple[int, int, int, int], None], Block], ...]
                full_block = []
                for sub_block_version, sub_block in block:
                    properties = sub_block.properties
                    if sub_block_version is None:
                        block_data = properties.get("block_data", amulet_nbt.TAG_Int(0))
                        if isinstance(block_data, amulet_nbt.TAG_Int):
                            block_data = block_data.value
                            if block_data >= 16:
                                block_data = 0
                        else:
                            block_data = 0
                        sub_block_ = amulet_nbt.NBTFile(
                            amulet_nbt.TAG_Compound(
                                {
                                    "name": amulet_nbt.TAG_String(
                                        sub_block.namespaced_name
                                    ),
                                    "val": amulet_nbt.TAG_Short(block_data),
                                }
                            )
                        )
                    else:
                        sub_block_ = amulet_nbt.NBTFile(
                            amulet_nbt.TAG_Compound(
                                {
                                    "name": amulet_nbt.TAG_String(
                                        sub_block.namespaced_name
                                    ),
                                    "states": amulet_nbt.TAG_Compound(
                                        {
                                            key: val
                                            for key, val in properties.items()
                                            if isinstance(val, amulet_nbt.BaseValueType)
                                        }
                                    ),
                                    "version": amulet_nbt.TAG_Int(
                                        sum(
                                            sub_block_version[i] << (24 - i * 8)
                                            for i in range(4)
                                        )
                                    ),
                                }
                            )
                        )

                    full_block.append(sub_block_)
                palette[index] = tuple(full_block)

            chunk = []
            for cy in range(16):
                if cy in blocks:
                    palette_index, sub_chunk = fast_unique(blocks.get_sub_chunk(cy))
                    sub_chunk_palette = palette[palette_index]
                    sub_chunk_depth = palette_depth[palette_index].max()

                    if (
                        sub_chunk_depth == 1
                        and len(sub_chunk_palette) == 1
                        and sub_chunk_palette[0][0]["name"].value == "minecraft:air"
                    ):
                        chunk.append(None)
                    else:
                        # pad palette with air in the extra layers
                        sub_chunk_palette_full = numpy.empty(
                            (sub_chunk_palette.size, sub_chunk_depth), dtype=object
                        )
                        sub_chunk_palette_full.fill(air)

                        for index, block_tuple in enumerate(sub_chunk_palette):
                            for sub_index, block in enumerate(block_tuple):
                                sub_chunk_palette_full[index, sub_index] = block
                        # should now be a 2D array with an amulet_nbt.NBTFile in each element

                        sub_chunk_bytes = [b"\x08", bytes([sub_chunk_depth])]
                        for sub_chunk_layer_index in range(sub_chunk_depth):
                            # TODO: sort out a way to do this quicker without brute forcing it.
                            (
                                sub_chunk_layer_palette,
                                sub_chunk_remap,
                            ) = brute_sort_objects_no_hash(
                                sub_chunk_palette_full[:, sub_chunk_layer_index]
                            )
                            sub_chunk_layer = sub_chunk_remap[sub_chunk.ravel()]

                            # sub_chunk_layer, sub_chunk_layer_palette = sub_chunk, sub_chunk_palette_full[:, sub_chunk_layer_index]
                            sub_chunk_bytes.append(
                                self._save_palette_subchunk(
                                    sub_chunk_layer.reshape(16, 16, 16),
                                    list(sub_chunk_layer_palette.ravel()),
                                )
                            )

                        chunk.append(b"".join(sub_chunk_bytes))
                else:
                    chunk.append(None)
        else:
            chunk = [None] * 16

        return chunk

    # These arent actual blocks, just ids pointing to the palette.

    @staticmethod
    def _load_palette_blocks(
        data
    ) -> Tuple[numpy.ndarray, List[amulet_nbt.NBTFile], bytes]:
        # Ignore LSB of data (its a flag) and get compacting level
        bits_per_block, data = data[0] >> 1, data[1:]
        blocks_per_word = 32 // bits_per_block  # Word = 4 bytes, basis of compacting.
        word_count = -(
            -4096 // blocks_per_word
        )  # Ceiling divide is inverted floor divide

        blocks = numpy.packbits(
            numpy.pad(
                numpy.unpackbits(
                    numpy.frombuffer(
                        bytes(reversed(data[: 4 * word_count])), dtype="uint8"
                    )
                )
                .reshape(-1, 32)[:, -blocks_per_word * bits_per_block:]
                .reshape(-1, bits_per_block)[-4096:, :],
                [(0, 0), (16 - bits_per_block, 0)],
                "constant",
            )
        ).view(dtype=">i2")[::-1]
        blocks = blocks.reshape((16, 16, 16)).swapaxes(1, 2)

        data = data[4 * word_count:]

        palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
        palette, offset = amulet_nbt.load(
            buffer=data,
            compressed=False,
            count=palette_len,
            offset=True,
            little_endian=True,
        )

        return blocks, palette, data[offset:]

    @staticmethod
    def _save_palette_subchunk(
        blocks: numpy.ndarray, palette: List[amulet_nbt.NBTFile]
    ) -> bytes:
        """Save a single layer of blocks in the palette format"""
        chunk: List[bytes] = []

        bits_per_block = max(int(numpy.amax(blocks)).bit_length(), 1)
        if bits_per_block == 7:
            bits_per_block = 8
        elif 9 <= bits_per_block <= 15:
            bits_per_block = 16
        chunk.append(bytes([bits_per_block << 1]))

        blocks_per_word = 32 // bits_per_block  # Word = 4 bytes, basis of compacting.
        word_count = -(
            -4096 // blocks_per_word
        )  # Ceiling divide is inverted floor divide

        blocks = blocks.swapaxes(1, 2).ravel()
        blocks = bytes(
            reversed(
                numpy.packbits(
                    numpy.pad(
                        numpy.pad(
                            numpy.unpackbits(
                                numpy.ascontiguousarray(blocks[::-1], dtype=">i").view(
                                    dtype="uint8"
                                )
                            ).reshape(4096, -1)[:, -bits_per_block:],
                            [(word_count * blocks_per_word - 4096, 0), (0, 0)],
                            "constant",
                        ).reshape(-1, blocks_per_word * bits_per_block),
                        [(0, 0), (32 - blocks_per_word * bits_per_block, 0)],
                        "constant",
                    )
                )
                .view(dtype=">i4")
                .tobytes()
            )
        )
        chunk.append(blocks)

        chunk.append(struct.pack("<I", len(palette)))
        chunk += [
            block.save_to(compressed=False, little_endian=True) for block in palette
        ]
        return b"".join(chunk)

    @staticmethod
    def _unpack_nbt_list(raw_nbt: bytes) -> List[amulet_nbt.NBTFile]:
        nbt_list = []
        while raw_nbt:
            nbt, index = amulet_nbt.load(
                buffer=raw_nbt, little_endian=True, offset=True
            )
            raw_nbt = raw_nbt[index:]
            nbt_list.append(nbt)
        return nbt_list

    @staticmethod
    def _pack_nbt_list(nbt_list: List[amulet_nbt.NBTFile]):
        return b"".join(
            [
                nbt.save_to(compressed=False, little_endian=True)
                for nbt in nbt_list
                if isinstance(nbt, amulet_nbt.NBTFile)
            ]
        )

    def _decode_entities(self, entities: List[amulet_nbt.NBTFile]) -> List[Entity]:
        entities_out = []
        for nbt in entities:
            entity = self._decode_entity(
                nbt,
                self.features["entity_format"],
                self.features["entity_coord_format"],
            )
            if entity is not None:
                entities_out.append(entity)

        return entities_out

    def _encode_entities(self, entities: EntityList) -> List[amulet_nbt.NBTFile]:
        entities_out = []
        for entity in entities:
            nbt = self._encode_entity(
                entity,
                self.features["entity_format"],
                self.features["entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt)

        return entities_out

    def _decode_block_entities(
        self, block_entities: List[amulet_nbt.NBTFile]
    ) -> List[BlockEntity]:
        entities_out = []
        for nbt in block_entities:
            entity = self._decode_block_entity(
                nbt,
                self.features["block_entity_format"],
                self.features["block_entity_coord_format"],
            )
            if entity is not None:
                entities_out.append(entity)

        return entities_out

    def _encode_block_entities(
        self, block_entities: Iterable[BlockEntity]
    ) -> List[amulet_nbt.NBTFile]:
        entities_out = []
        for entity in block_entities:
            nbt = self._encode_block_entity(
                entity,
                self.features["block_entity_format"],
                self.features["block_entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt)

        return entities_out

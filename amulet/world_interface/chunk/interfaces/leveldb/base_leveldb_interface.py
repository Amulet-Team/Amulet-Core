from __future__ import annotations

from typing import Tuple, Dict, List, Union

import struct
import numpy
import amulet_nbt

from amulet.api.block import Block
from amulet.api.chunk import Chunk
from amulet.utils.world_utils import get_smallest_dtype
from amulet.world_interface.chunk.interfaces import Interface
from amulet.world_interface.chunk import translators
from amulet.world_interface.chunk.interfaces.leveldb.leveldb_chunk_versions import chunk_to_game_version, game_to_chunk_version


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


class BaseLevelDBInterface(Interface):
    def __init__(self):
        feature_options = {
            "chunk_version": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "finalised_state": [],
            "data_2d": [],
            "entities": ["32list"],
            "block_entities": ["31list"],
            "terrain": ["2farray", "2f1palette", "2fnpalette"]
        }
        self.features = {key: None for key in feature_options.keys()}

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
            chunk_version = data[b'v'][0]
            game_version = chunk_to_game_version(max_world_version[1], chunk_version)
        else:
            game_version = max_world_version[1]
        return translators.loader.get(("leveldb", game_version)), game_version

    def decode(self, cx: int, cz: int, data: Dict[bytes, bytes]) -> Tuple[Chunk, numpy.ndarray]:
        # chunk_key_base = struct.pack("<ii", cx, cz)

        chunk = Chunk(cx, cz)

        if self.features["terrain"] in ["2farray", "2f1palette", "2fnpalette"]:
            subchunks = [data.get(b"\x2F" + bytes([i]), None) for i in range(16)]
            chunk.blocks, palette = self._load_subchunks(subchunks)
        else:
            raise Exception

        chunk.entities = None
        chunk.block_entities = None
        return chunk, palette

    def encode(
        self,
        chunk: Chunk,
        palette: numpy.ndarray,
        max_world_version: Tuple[int, int, int],
    ) -> Dict[bytes, bytes]:
        chunk_data = {}
        if self.features['terrain'] == '2farray':
            terrain = self._save_subchunks_0(chunk.blocks, palette)
        elif self.features['terrain'] == '2f1palette':
            terrain = self._save_subchunks_1(chunk.blocks, palette)
        elif self.features['terrain'] == '2fnpalette':
            terrain = self._save_subchunks_8(chunk.blocks, palette)
        else:
            raise Exception
        for y, sub_chunk in enumerate(terrain):
            chunk_data[b"\x2F" + bytes([y])] = sub_chunk

        chunk_data[b'v'] = bytes([self.features["chunk_version"]])

        return chunk_data

    def _load_subchunks(self, subchunks: List[None, bytes]) -> Tuple[numpy.ndarray, numpy.ndarray]:
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

        blocks = numpy.zeros((16, 256, 16), dtype=numpy.uint32)
        palette: List[
            Tuple[
                Tuple[
                    Union[None, Tuple[int, int, int, int]],
                    Union[Tuple[int, int], Block]
                ]
            ]
        ] = [
            (
                (
                    (1, 7, 0, 0),
                    Block(namespace="minecraft", base_name="air", properties={"block_data": 0})
                ),
            )
        ]
        for y, data in enumerate(subchunks):
            if data is None:
                continue
            if data[0] in [0, 2, 3, 4, 5, 6, 7]:
                raise NotImplementedError
            elif data[0] in [1, 8]:
                if data[0] == 1:
                    storage_count = 1
                    data = data[1:]
                else:
                    storage_count, data = data[1], data[2:]

                sub_chunk_blocks = numpy.zeros((16, 16, 16, storage_count), dtype=numpy.int)
                sub_chunk_palette: List[List[Tuple[Union[None, Tuple[int, int, int, int]], Block]]] = []
                for storage_index in range(storage_count):
                    sub_chunk_blocks[:, :, :, storage_index], palette_data, data = self._load_palette_blocks(data)
                    palette_data_out: List[Tuple[Union[None, Tuple[int, int, int, int]], Block]] = []
                    for block in palette_data:
                        namespace, base_name = block["name"].value.split(":", 1)
                        if 'version' in block:
                            version = tuple(numpy.array([block['version'].value], dtype='>u4').view(numpy.uint8))
                        else:
                            version = None

                        if "states" in block:  # 1.13 format
                            properties = block["states"].value
                        else:
                            properties = {"block_data": str(block["val"].value)}
                        palette_data_out.append(
                            (
                                version,
                                Block(namespace=namespace, base_name=base_name, properties=properties)
                            )
                        )
                    sub_chunk_palette.append(palette_data_out)

                y *= 16
                if storage_count == 1:
                    blocks[:, y: y + 16, :] = sub_chunk_blocks[:, :, :, 0] + len(palette)
                    palette += [(val,) for val in sub_chunk_palette[0]]
                elif storage_count > 1:
                    # we have two or more storages so need to find the unique block combinations and merge them together
                    sub_chunk_palette_, sub_chunk_blocks = numpy.unique(sub_chunk_blocks.reshape(-1, storage_count), return_inverse=True, axis=0)
                    blocks[:, y: y + 16, :] = sub_chunk_blocks.reshape(16, 16, 16) + len(palette)
                    palette += [
                        tuple(
                            sub_chunk_palette[storage_index][index]
                            for storage_index, index in enumerate(palette_indexes)
                            if not (storage_index > 0 and sub_chunk_palette[storage_index][index][1].namespaced_name == 'minecraft:air')
                        )
                        for palette_indexes in sub_chunk_palette_
                    ]
                else:
                    raise Exception('Is a chunk with no storages allowed?')
                # palette should now look like this
                # List[
                #   Tuple[
                #       Tuple[version, Block]
                #   ]
                # ]

        numpy_palette, inverse = brute_sort_objects(palette)
        blocks = inverse[blocks]

        return blocks.astype(f"uint{get_smallest_dtype(blocks)}"), numpy_palette

    def _save_subchunks_0(self, blocks: numpy.ndarray, palette: numpy.ndarray) -> List[Union[None, bytes]]:
        raise NotImplementedError

    def _save_subchunks_1(self, blocks: numpy.ndarray, palette: numpy.ndarray) -> List[Union[None, bytes]]:
        for index, block in enumerate(palette):
            block: Tuple[
                Tuple[None, Block], ...
            ]
            block_data = block[0][1].properties.get('block_data', '0')
            if isinstance(block_data, str) and block_data.isnumeric():
                block_data = int(block_data)
                if block_data >= 16:
                    block_data = 0
            else:
                block_data = 0

            palette[index] = amulet_nbt.NBTFile(
                amulet_nbt.TAG_Compound({
                    'name': amulet_nbt.TAG_String(block[0][1].namespaced_name),
                    'val': amulet_nbt.TAG_Short(block_data)
                })
            )
        chunk = []
        for y in range(0, 256, 16):
            palette_index, sub_chunk = numpy.unique(blocks[:, y:y+16, :], return_inverse=True)
            sub_chunk_palette = list(palette[palette_index])
            chunk.append(b'\x01' + self._save_palette_subchunk(sub_chunk, sub_chunk_palette))
        return chunk

    def _save_subchunks_8(self, blocks: numpy.ndarray, palette: numpy.ndarray) -> List[Union[None, bytes]]:
        palette_depth = numpy.array([len(block) for block in palette])
        if palette[0][0][0] is None:
            air = amulet_nbt.NBTFile(
                amulet_nbt.TAG_Compound({
                    'name': amulet_nbt.TAG_String('minecraft:air'),
                    'val': amulet_nbt.TAG_Short(0)
                })
            )
        else:
            air = amulet_nbt.NBTFile(
                amulet_nbt.TAG_Compound({
                    'name': amulet_nbt.TAG_String('minecraft:air'),
                    'states': amulet_nbt.TAG_Compound({}),
                    'version': amulet_nbt.TAG_Int(17629184)
                })
            )

        for index, block in enumerate(palette):
            block: Tuple[
                Tuple[Union[Tuple[int, int, int, int], None], Block], ...
            ]
            full_block = []
            for sub_block_version, sub_block in block:
                properties = sub_block.properties
                if sub_block_version is None:
                    block_data = properties.get('block_data', '0')
                    if isinstance(block_data, str) and block_data.isnumeric():
                        block_data = int(block_data)
                        if block_data >= 16:
                            block_data = 0
                    else:
                        block_data = 0
                    sub_block_ = amulet_nbt.NBTFile(
                        amulet_nbt.TAG_Compound({
                            'name': amulet_nbt.TAG_String(sub_block.namespaced_name),
                            'val': amulet_nbt.TAG_Short(block_data)
                        })
                    )
                else:
                    sub_block_ = amulet_nbt.NBTFile(
                        amulet_nbt.TAG_Compound({
                            'name': amulet_nbt.TAG_String(sub_block.namespaced_name),
                            'states': amulet_nbt.TAG_Compound({key: val for key, val in properties.values() if isinstance(val, amulet_nbt._TAG_Value)}),
                            'version': amulet_nbt.TAG_Int(sum(sub_block_version[i] << (24-i*8) for i in range(4)))
                        })
                    )

                full_block.append(sub_block_)
            palette[index] = tuple(full_block)

        chunk = []
        for y in range(0, 256, 16):
            palette_index, sub_chunk = numpy.unique(blocks[:, y:y + 16, :], return_inverse=True)
            sub_chunk_palette = palette[palette_index]
            sub_chunk_depth = palette_depth[palette_index].max()

            if sub_chunk_depth == 1 and len(sub_chunk_palette) == 1 and sub_chunk_palette[0][0]['name'].value == 'minecraft:air':
                chunk.append(None)
            else:
                # pad palette with air in the extra layers
                sub_chunk_palette_full = numpy.full((sub_chunk_palette.size, sub_chunk_depth), air, dtype=object)
                # sub_chunk_palette_full[:, :] = air

                for index, block_tuple in enumerate(sub_chunk_palette):
                    for sub_index, block in enumerate(block_tuple):
                        sub_chunk_palette_full[index, sub_index] = block
                # should now be a 2D array with an amulet_nbt.NBTFile in each element

                # sub_chunk_bytes = [b'\x08', bytes([sub_chunk_depth])]
                sub_chunk_bytes = [b'\x08', bytes([1])]
                for sub_chunk_layer_index in range(1):      # range(sub_chunk_depth):  # TODO: fix the second layer not being translated
                    # TODO: sort out a way to remove duplicate NBTFile objects. Currently the features to sort or check for duplicates do not exist
                    # sub_chunk_layer_palette, sub_chunk_remap = numpy.unique(sub_chunk_palette_full[:, sub_chunk_layer], return_inverse=True)
                    # sub_chunk_layer = sub_chunk_remap[sub_chunk]

                    sub_chunk_layer, sub_chunk_layer_palette = sub_chunk, sub_chunk_palette_full[:, sub_chunk_layer_index]
                    sub_chunk_bytes.append(self._save_palette_subchunk(sub_chunk_layer.reshape(16, 16, 16), list(sub_chunk_layer_palette.ravel())))

                chunk.append(b''.join(sub_chunk_bytes))

        return chunk

    # These arent actual blocks, just ids pointing to the palette.
    def _load_palette_blocks(self, data) -> Tuple[numpy.ndarray, List[amulet_nbt.NBTFile], bytes]:
        # Ignore LSB of data (its a flag) and get compacting level
        bits_per_block, data = data[0] >> 1, data[1:]
        blocks_per_word = 32 // bits_per_block  # Word = 4 bytes, basis of compacting.
        word_count = -(-4096 // blocks_per_word)  # Ceiling divide is inverted floor divide

        blocks = numpy.packbits(
            numpy.pad(
                numpy.unpackbits(
                    numpy.frombuffer(bytes(reversed(data[: 4 * word_count])), dtype='uint8')
                ).reshape(-1, 32)[:, -blocks_per_word*bits_per_block:].reshape(-1, bits_per_block)[-4096:, :],
                [(0, 0), (16 - bits_per_block, 0)],
                "constant"
            )
        ).view(dtype=">i2")[::-1]
        blocks = blocks.reshape((16, 16, 16)).swapaxes(1, 2)

        data = data[4 * word_count:]

        palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
        palette, offset = amulet_nbt.load(
            buffer=data, compressed=False, count=palette_len, offset=True  # , little_endian=True
        )

        return blocks, palette, data[offset:]

    def _save_palette_subchunk(self, blocks: numpy.ndarray, palette: List[amulet_nbt.NBTFile]) -> bytes:
        """Save a single layer of blocks in the palette format"""
        chunk: List[bytes] = []

        bits_per_block = max(int(blocks.max()).bit_length(), 1)
        if bits_per_block == 7:
            bits_per_block = 8
        elif 9 <= bits_per_block <= 15:
            bits_per_block = 16
        chunk.append(bytes([bits_per_block << 1]))

        blocks_per_word = 32 // bits_per_block  # Word = 4 bytes, basis of compacting.
        word_count = -(-4096 // blocks_per_word)  # Ceiling divide is inverted floor divide

        blocks = blocks.swapaxes(1, 2).ravel()
        blocks = bytes(reversed(numpy.packbits(
            numpy.pad(
                numpy.pad(
                    numpy.unpackbits(
                        numpy.ascontiguousarray(blocks[::-1], dtype='>i').view(dtype='uint8')
                    ).reshape(4096, -1)[:, -bits_per_block:],
                    [(word_count*blocks_per_word-4096, 0), (0, 0)],
                    "constant"
                ).reshape(-1, blocks_per_word*bits_per_block),
                [(0, 0), (32-blocks_per_word*bits_per_block, 0)],
                "constant"
            )
        ).view(dtype=">i4").tobytes()))
        chunk.append(blocks)

        chunk.append(struct.pack("<I", len(palette)))
        chunk += [block.save_to(compressed=False, little_endian=True) for block in palette]
        return b''.join(chunk)


from __future__ import annotations

from typing import Tuple, Dict, List, Union

import struct
import numpy
import amulet_nbt

from amulet.api.block import Block
from amulet.api.chunk import Chunk
from amulet.world_interface.chunk.interfaces.leveldb.base_leveldb_interface import BaseLevelDBInterface
from amulet.utils.world_utils import get_smallest_dtype


class LevelDBInterface(BaseLevelDBInterface):
    @staticmethod
    def is_valid(key):
        if key[0] != "leveldb":
            return False
        if key[1] not in [10, 13, 14, 15]:
            return False
        return True

    def decode(self, cx: int, cz: int, data: Dict[bytes, bytes]) -> Tuple[Chunk, numpy.ndarray]:
        # chunk_key_base = struct.pack("<ii", cx, cz)

        subchunks = []
        for i in range(16):
            subchunks.append(data.get(b"\x2F" + bytes([i]), None))

        chunk = Chunk(cx, cz)
        chunk.blocks, palette = self._load_subchunks(subchunks)
        chunk.entities = None
        chunk.block_entities = None
        return chunk, palette

    def encode(
        self,
        chunk: Chunk,
        palette: numpy.ndarray,
        max_world_version: Tuple[int, int, int],
    ) -> Dict[bytes, bytes]:
        raise NotImplementedError

    def _load_subchunks(self, subchunks: List[None, bytes]):
        blocks = numpy.zeros((16, 256, 16), dtype=numpy.uint32)
        palette: List[Tuple[Tuple[Union[None, Tuple[int, int, int, int]], Block]]] = [
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
            version, numStorages, data = data[0], data[1], data[2:]
            sub_chunk_blocks = numpy.zeros((16, 16, 16, numStorages), dtype=numpy.int)
            sub_chunk_palette: List[List[Tuple[Union[None, Tuple[int, int, int, int]], Block]]] = []
            for storage_index in range(numStorages):
                sub_chunk_blocks[:, :, :, storage_index], data = self._load_blocks(data)
                palette_data, data = self._load_palette(data)
                for i, block in enumerate(palette_data):
                    namespace, base_name = block["name"].value.split(":", 1)
                    if 'version' in block:
                        version = tuple(numpy.array([block['version'].value], dtype='>u4').view(numpy.uint8))
                    else:
                        version = None

                    if "states" in block:  # 1.13 format
                        properties = block["states"].value
                    else:
                        properties = {"block_data": str(block["val"].value)}
                    palette_data[i] = version, Block(
                        namespace=namespace, base_name=base_name, properties=properties
                    )
                sub_chunk_palette.append(palette_data)

            y *= 16
            if numStorages == 1:
                blocks[:, y: y + 16, :] = sub_chunk_blocks[:, :, :, 0] + len(palette)
                palette += [(val,) for val in sub_chunk_palette[0]]
            elif numStorages > 1:
                # we have two or more storages so need to find the unique block combinations and merge them together
                sub_chunk_palette_, sub_chunk_blocks = numpy.unique(sub_chunk_blocks.reshape(-1, numStorages), return_inverse=True, axis=0)
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
        p = numpy.empty(len(palette), dtype=object)
        for i, val in enumerate(palette):
            p[i] = val
        numpy_palette, inverse = numpy.unique(p, return_inverse=True)
        blocks = inverse[blocks]

        return blocks.astype(f"uint{get_smallest_dtype(blocks)}"), numpy_palette

    # These arent actual blocks, just ids pointing to the palette.
    def _load_blocks(self, data):
        # Ignore LSB of data (its a flag) and get compacting level
        bitsPerBlock, data = data[0] >> 1, data[1:]
        blocksPerWord = 32 // bitsPerBlock  # Word = 4 bytes, basis of compacting.
        numWords = -(-4096 // blocksPerWord)  # Ceiling divide is inverted floor divide

        blockWords, data = (
            struct.unpack("<" + "I" * numWords, data[: 4 * numWords]),
            data[4 * numWords :],
        )
        blocks = numpy.empty(4096, dtype=numpy.uint32)
        for i, word in enumerate(blockWords):
            for j in range(blocksPerWord):
                block = word & (
                    (1 << bitsPerBlock) - 1
                )  # Mask out number of bits for one block
                word >>= bitsPerBlock  # For next iteration
                if i * blocksPerWord + j < 4096:  # Safety net for padding at end.
                    blocks[i * blocksPerWord + j] = block
        blocks = blocks.reshape((16, 16, 16)).swapaxes(1, 2)
        return blocks, data

    # NBT encoded block names (with minecraft:) and data values.
    def _load_palette(self, data):
        palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
        palette, offset = amulet_nbt.load(
            buffer=data, compressed=False, count=palette_len, offset=True
        )
        return palette, data[offset:]


INTERFACE_CLASS = LevelDBInterface

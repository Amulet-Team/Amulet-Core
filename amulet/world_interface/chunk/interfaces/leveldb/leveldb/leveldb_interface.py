from __future__ import annotations

from typing import Tuple, Dict, List

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
        palette = [
            Block(namespace="minecraft", base_name="air", properties={"block_data": 0})
        ]
        for y, data in enumerate(subchunks):
            if data is None:
                continue
            version, numStorages, data = data[0], data[1], data[2:]
            block_data, data = self._load_blocks(data)
            palette_data = self._load_palette(data)
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
            y *= 16
            blocks[:, y: y + 16, :] = block_data + len(palette)
            palette += palette_data

        palette, inverse = numpy.unique(palette, return_inverse=True)
        blocks = inverse[blocks]

        return blocks.astype(f"uint{get_smallest_dtype(blocks)}"), palette

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
        blocks = blocks.reshape(16, 16, 16).swapaxes(1, 2)
        return blocks, data

    # NBT encoded block names (with minecraft:) and data values.
    def _load_palette(self, data):
        palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
        palette, offset = amulet_nbt.load(
            buffer=data, compressed=False, count=palette_len, offset=True
        )
        return palette


INTERFACE_CLASS = LevelDBInterface

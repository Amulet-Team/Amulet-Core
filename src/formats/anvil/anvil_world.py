from __future__ import annotations

import struct
import zlib
from io import BytesIO
from typing import Tuple, Union

import numpy

from api import WorldFormat
from nbt import nbt
from os import path

from api.world import World
from api.blocks import Block, BlockManager
from utils.world_utils import get_smallest_dtype
from version_definitions.definition_manager import DefinitionManager

from utils import world_utils


class _AnvilRegionManager:
    def __init__(self, directory: str):
        self._directory = directory
        self._loaded_regions = {}

    def load_chunk(
        self, cx: int, cz: int
    ) -> Tuple[nbt.TAG_List, nbt.TAG_List, nbt.TAG_List]:
        rx, rz = world_utils.chunk_coords_to_region_coords(cx, cz)
        key = (rx, rz)

        if key not in self._loaded_regions:
            if not self.load_region(rx, rz):
                raise Exception()

        cx &= 0x1F
        cz &= 0x1F

        chunk_offset = self._loaded_regions[key]["offsets"][
            (cx & 0x1F) + (cz & 0x1F) * 32
        ]
        if chunk_offset == 0:
            raise Exception()

        sector_start = chunk_offset >> 8
        number_of_sectors = chunk_offset & 0xFF

        if number_of_sectors == 0:
            raise Exception()

        if sector_start + number_of_sectors > len(
            self._loaded_regions[key]["free_sectors"]
        ):
            raise Exception()

        fp = open(
            path.join(self._directory, "region", "r.{}.{}.mca".format(rx, rz)), "rb"
        )
        fp.seek(sector_start * world_utils.SECTOR_BYTES)
        data = fp.read(number_of_sectors * world_utils.SECTOR_BYTES)
        fp.close()

        if len(data) < 5:
            raise Exception("Malformed sector/chunk")

        length = struct.unpack_from(">I", data)[0]
        _format = struct.unpack_from("B", data, 4)[0]
        data = data[5 : length + 5]

        if _format == world_utils.VERSION_GZIP:
            data = world_utils.gunzip(data)
        elif _format == world_utils.VERSION_DEFLATE:
            data = zlib.decompress(data)

        nbt_data = nbt.NBTFile(buffer=BytesIO(data))

        return (
            nbt_data["Level"]["Sections"],
            nbt_data["Level"]["TileEntities"],
            nbt_data["Level"]["Entities"],
        )

    def load_region(self, rx: int, rz: int) -> bool:
        key = (rx, rz)
        if key in self._loaded_regions:
            return True

        filename = path.join(self._directory, "region", "r.{}.{}.mca".format(rx, rz))
        if not path.exists(filename):
            raise FileNotFoundError()

        with open(filename, "rb") as fp:
            self._loaded_regions[key] = {}

            file_size = path.getsize(filename)
            if file_size & 0xFFF:
                file_size = (file_size | 0xFFF) + 1
                fp.truncate(file_size)

            if not file_size:
                file_size = world_utils.SECTOR_BYTES * 2
                fp.truncate(file_size)

            self._loaded_regions[key]["file_size"] = file_size

            fp.seek(0)

            offsets = fp.read(world_utils.SECTOR_BYTES)
            mod_times = fp.read(world_utils.SECTOR_BYTES)

            self._loaded_regions[key]["free_sectors"] = free_sectors = [True] * (
                file_size // world_utils.SECTOR_BYTES
            )
            self._loaded_regions[key]["free_sectors"][0:2] = False, False

            self._loaded_regions[key]["offsets"] = offsets = numpy.frombuffer(
                offsets, dtype=">u4"
            )
            self._loaded_regions[key]["mod_times"] = numpy.frombuffer(
                mod_times, dtype=">u4"
            )

            for offset in offsets:
                sector = offset >> 8
                count = offset & 0xFF

                for i in range(sector, sector + count):
                    if i >= len(free_sectors):
                        return False

                    free_sectors[i] = False

        return True


class AnvilWorld(WorldFormat):
    def __init__(self, directory: str, definitions: str, adapters):
        super(AnvilWorld, self).__init__(adapters)
        self._directory = directory
        self._materials = DefinitionManager(definitions)
        self._region_manager = _AnvilRegionManager(directory)
        self.mapping_handler = BlockManager()
        self.unknown_blocks = {}

    @classmethod
    def load(cls, directory: str, definitions: str, adapters) -> World:
        wrapper = cls(directory, definitions, adapters)
        fp = open(path.join(directory, "level.dat"), "rb")
        root_tag = nbt.NBTFile(fileobj=fp)
        fp.close()

        return World(directory, root_tag, wrapper)

    def get_blocks(self, cx: int, cz: int) -> Union[numpy.ndarray, NotImplementedError]:
        chunk_sections, _, _ = self._region_manager.load_chunk(cx, cz)
        if len(chunk_sections) == 0:
            return NotImplementedError(
                "We don't support reading chunks that never been edited in Minecraft before"
            )

        blocks = numpy.zeros((256, 16, 16), dtype=int)
        block_data = numpy.zeros((256, 16, 16), dtype=numpy.uint8)
        for section in chunk_sections:
            lower = section["Y"].value << 4
            upper = (section["Y"].value + 1) << 4

            section_blocks = numpy.frombuffer(
                section["Blocks"].value, dtype=numpy.uint8
            )
            section_data = numpy.frombuffer(section["Data"].value, dtype=numpy.uint8)
            section_blocks = section_blocks.reshape((16, 16, 16))
            section_blocks.astype(numpy.uint16, copy=False)

            section_data = section_data.reshape(
                (16, 16, 8)
            )  # The Byte array is actually just Nibbles, so the size is off

            section_data = world_utils.from_nibble_array(section_data)

            if "Add" in section:
                add_blocks = numpy.frombuffer(section["Add"].value, dtype=numpy.uint8)
                add_blocks = add_blocks.reshape((16, 16, 8))
                add_blocks = world_utils.from_nibble_array(add_blocks)

                section_blocks |= add_blocks.astype(numpy.uint16) << 8

            blocks[lower:upper, :, :] = section_blocks
            block_data[lower:upper, :, :] = section_data

        blocks = numpy.swapaxes(blocks.swapaxes(0, 1), 0, 2)
        block_data_array = numpy.swapaxes(block_data.swapaxes(0, 1), 0, 2)

        unique_block_ids = numpy.unique(
            blocks
        )  # Flatten the 3D array into 1D and remove all duplicate entries
        # unique_block_ids = unique_block_ids[
        #    unique_block_ids != 0
        # ]  # Remove all air entries

        unique_blocks = set()
        for (
            block_id
        ) in (
            unique_block_ids
        ):  # Find all instances of the base ID and find any occurrences of data values
            indices = numpy.where(blocks == block_id)

            for block_data in numpy.unique(block_data_array[indices]):
                unique_blocks.add((block_id, block_data))

        block_test = numpy.zeros_like(blocks, dtype=int)
        for block in unique_blocks:
            internal = self._materials.get_block_from_definition(
                block, default="minecraft:unknown_{}"
            )
            block_object: Block = self.get_blockstate(internal)
            if (
                internal == "minecraft:unknown_{}"
            ):  # If we don't have the block in our definitions, call it an unknown block
                try:
                    internal_id = list(self.unknown_blocks.values()).index(block)
                except ValueError:
                    block_object: Block = Block(
                        blockstate=f"minecraft:unknown_{len(self.unknown_blocks)}"
                    )
                    internal_id = self.mapping_handler[block_object]
                    self.unknown_blocks[internal_id] = block
            else:
                internal_id = self.mapping_handler[
                    block_object
                ]  # Find the index of the block in mapping_handler

            block_mask = blocks == block[0]
            data_mask = block_data_array == block[1]

            mask = (
                block_mask & data_mask
            )  # Combine the mask from the base ID array and the data value array

            block_test[
                mask
            ] = internal_id  # Mask all occurrences and set them to the internal ID

        block_test = block_test.astype(
            f"uint{get_smallest_dtype(block_test)}"
        )  # Shrink the array's dtype as needed
        return block_test

    @classmethod
    def from_unified_format(cls, unified: World) -> WorldFormat:
        pass

    def save(self) -> None:
        pass

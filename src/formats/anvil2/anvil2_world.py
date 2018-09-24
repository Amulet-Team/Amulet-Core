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
from utils.world_utils import get_smallest_dtype
from version_definitions.definition_manager import DefinitionManager

from utils import world_utils


class _Anvil2RegionManager:
    def __init__(self, directory: str):
        self._directory = directory
        self._loaded_regions = {}

    def load_chunk(
        self, cx: int, cz: int
    ) -> Tuple[nbt.TAG_List, nbt.TAG_List, nbt.TAG_List]:
        rx, rz = world_utils.chunk_coords_to_region_coords(cx, cz)
        key = (rx, rz)

        if not self.load_region(rx, rz):
            raise Exception()

        cx &= 0x1f
        cz &= 0x1f

        chunk_offset = self._loaded_regions[key]["offsets"][
            (cx & 0x1f) + (cz & 0x1f) * 32
        ]
        if chunk_offset == 0:
            raise Exception()

        sector_start = chunk_offset >> 8
        number_of_sectors = chunk_offset & 0xff

        if number_of_sectors == 0:
            raise Exception()

        if sector_start + number_of_sectors > len(
            self._loaded_regions[key]["free_sectors"]
        ):
            raise Exception()

        with open(
            path.join(self._directory, "region", "r.{}.{}.mca".format(rx, rz)), "rb"
        ) as fp:
            fp.seek(sector_start * world_utils.SECTOR_BYTES)
            data = fp.read(number_of_sectors * world_utils.SECTOR_BYTES)

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

        fp = open(filename, "rb")
        self._loaded_regions[key] = {}

        file_size = path.getsize(filename)
        if file_size & 0xfff:
            file_size = (file_size | 0xfff) + 1
            fp.truncate(file_size)

        if not file_size:
            file_size = world_utils.SECTOR_BYTES * 2
            fp.truncate(file_size)

        self._loaded_regions[key]["file_size"] = file_size

        fp.seek(0)

        offsets = fp.read(world_utils.SECTOR_BYTES)
        mod_times = fp.read(world_utils.SECTOR_BYTES)

        self._loaded_regions[key]["free_sectors"] = free_sectors = numpy.full(
            file_size // world_utils.SECTOR_BYTES, True, bool
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
            count = offset & 0xff

            for i in range(sector, sector + count):
                if i >= len(free_sectors):
                    return False

                free_sectors[i] = False

        fp.close()

        return True


class Anvil2World(WorldFormat):
    def __init__(self, directory: str, definitions: str):
        self._directory = directory
        self._materials = DefinitionManager(definitions)
        self._region_manager = _Anvil2RegionManager(directory)
        self.mapping_handler = numpy.unique(
            numpy.array(
                ["minecraft:air"] + [k for k in self._materials.blocks.keys()],
                dtype="object",
            )
        )

    @classmethod
    def load(cls, directory: str, definitions: str) -> World:
        wrapper = cls(directory, definitions)
        fp = open(path.join(directory, "level.dat"), "rb")
        root_tag = nbt.NBTFile(fileobj=fp)
        fp.close()

        return World(directory, root_tag, wrapper)

    def __read_palette(self, palette: nbt.TAG_List) -> list:
        blockstates = []
        for entry in palette:
            name = entry["Name"].value
            properties = self._materials.properties_to_string(
                entry.get("Properties", {})
            )
            if properties:
                blockstates.append(f"{name}[{properties}]")
            else:
                blockstates.append(name)
        return blockstates

    def get_blocks(self, cx: int, cz: int) -> Union[numpy.ndarray, NotImplementedError]:
        chunk_sections, _, _ = self._region_manager.load_chunk(cx, cz)
        if len(chunk_sections) == 0:
            return NotImplementedError(
                "We don't support reading chunks that never been edited in Minecraft before"
            )

        blocks = numpy.zeros((16, 256, 16), dtype=int)
        temp_blocks = numpy.full((256, 16, 16), "minecraft:air", dtype="object")
        uniques = numpy.array([])

        for section in chunk_sections:
            lower = section["Y"].value << 4
            upper = (section["Y"].value + 1) << 4

            palette = self.__read_palette(section["Palette"])

            blockstate_array = section["BlockStates"].value
            blockstate_array = numpy.array(blockstate_array, dtype=">q")
            bits_per_block = len(blockstate_array) // 64
            binary_blocks = numpy.unpackbits(
                blockstate_array[::-1].astype(">i8").view("uint8")
            ).reshape(-1, bits_per_block)
            before_palette = binary_blocks.dot(
                2 ** numpy.arange(binary_blocks.shape[1] - 1, -1, -1)
            )[::-1]

            _blocks = numpy.asarray(palette, dtype="object")[before_palette]

            uniques = numpy.append(uniques, numpy.unique(_blocks))
            temp_blocks[lower:upper, :, :] = _blocks.reshape((16, 16, 16))

        temp_blocks = numpy.swapaxes(temp_blocks.swapaxes(0, 1), 0, 2)

        uniques = numpy.unique(uniques)
        uniques = uniques[uniques != "minecraft:air"]
        for unique in uniques:
            internal = self._materials.get_block_from_definition(unique, default=unique)
            internal_in_mapping = numpy.where(self.mapping_handler == internal)[0]
            if len(internal_in_mapping) > 0:
                internal_id = internal_in_mapping[0]
            else:
                internal_id = len(self.mapping_handler)
                self.mapping_handler = numpy.append(self.mapping_handler, internal)

            mask = temp_blocks == unique

            blocks[mask] = internal_id

        blocks = blocks.astype(f"uint{get_smallest_dtype(blocks)}")
        return blocks

    @classmethod
    def from_unified_format(cls, unified: World) -> WorldFormat:
        pass

    def save(self) -> None:
        pass

from __future__ import annotations

import os
import struct
import zlib
from typing import Tuple, Any

import amulet_nbt as nbt
import numpy

from amulet.world_interface.formats import Format
from amulet.utils import world_utils
from amulet.utils.format_utils import check_all_exist, check_one_exists, load_leveldat


class AnvilRegionManager:
    def __init__(self, directory: str):
        self._directory = directory
        self._loaded_regions = {}

    def load_chunk_data(
        self, cx: int, cz: int
    ) -> nbt.NBTFile:
        rx, rz = world_utils.chunk_coords_to_region_coords(cx, cz)
        key = (rx, rz)

        if not self.load_region(rx, rz):
            raise Exception()

        cx &= 0x1F
        cz &= 0x1F

        chunk_offset = self._loaded_regions[key]["offsets"][
            (cx & 0x1F) + (cz & 0x1F) << 5
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

        with open(
            os.path.join(self._directory, "region", "r.{}.{}.mca".format(rx, rz)), "rb"
        ) as fp:
            fp.seek(sector_start * world_utils.SECTOR_BYTES)
            data = fp.read(number_of_sectors * world_utils.SECTOR_BYTES)

        if len(data) < 5:
            raise Exception("Malformed sector/chunk")

        length = struct.unpack_from(">I", data)[0]
        _format = struct.unpack_from("B", data, 4)[0]
        data = data[5: length + 5]

        if _format == world_utils.VERSION_GZIP:
            data = world_utils.gunzip(data)
        elif _format == world_utils.VERSION_DEFLATE:
            data = zlib.decompress(data)

        nbt_data = nbt.load(buffer=data)

        return nbt_data

    def load_region(self, rx: int, rz: int) -> bool:
        key = (rx, rz)
        if key in self._loaded_regions:
            return True

        filename = os.path.join(self._directory, "region", "r.{}.{}.mca".format(rx, rz))
        if not os.path.exists(filename):
            raise FileNotFoundError()

        fp = open(filename, "rb")
        self._loaded_regions[key] = {}

        file_size = os.path.getsize(filename)
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
            count = offset & 0xFF

            for i in range(sector, sector + count):
                if i >= len(free_sectors):
                    return False

                free_sectors[i] = False

        fp.close()

        return True


class AnvilFormat(Format):
    def __init__(self, *args):
        super().__init__(*args)
        self.root_tag = nbt.load(filename=os.path.join(self._directory, "level.dat"))
        self._region_manager = AnvilRegionManager(self._directory)

    def _load_chunk_data(self, cx, cz) -> Tuple[Tuple, Any]:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        nbt_data = self._region_manager.load_chunk_data(cx, cz)
        interface_key = ("anvil", nbt_data["DataVersion"].value)
        return interface_key, nbt_data

    @staticmethod
    def is_valid(directory) -> bool:
        print(directory)
        if not check_all_exist(directory, "region", "level.dat"):
            return False

        if not check_one_exists(directory, "playerdata", "players"):
            return False

        level_dat_root = load_leveldat(directory)

        if "FML" in level_dat_root:
            return False

        return True


FORMAT_CLASS = AnvilFormat

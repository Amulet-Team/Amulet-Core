from __future__ import annotations

import os
import struct
import zlib
import gzip
from typing import Tuple, Any, Dict
import numpy
import time

import amulet_nbt as nbt

from amulet.world_interface.formats import Format
from amulet.utils import world_utils
from amulet.utils.format_utils import check_all_exist, check_one_exists, load_leveldat
from amulet.world_interface.chunk import interfaces
from amulet.api.errors import ChunkDoesNotExist


class AnvilRegion:
    def __init__(self, file_path: str, create=False):
        self._file_path = file_path

        # [dirty, mod_time, data_length, data]  feel free to extend if you want to implement modifying in place and defragging
        self._chunks: Dict[Tuple[int, int], Tuple[bool, int, int, bytes]] = {}
        # self._file_size = 0
        # self._free_sectors = None     # implement these for modifying in place
        # self._offsets = None
        # self._mod_times = None
        self._dirty = False  # is a chunk in region dirty

        if not create:
            self._load()

    def _load(self):
        with open(self._file_path, "rb") as fp:
            # check that the file is a multiple of 4096 bytes and extend if not
            # TODO: perhaps rewrite this in a way that is more readable
            file_size = os.path.getsize(self._file_path)
            if file_size & 0xFFF:
                file_size = (file_size | 0xFFF) + 1
                fp.truncate(file_size)

            # if the length of the region file is 0 extend it to 8KiB TODO (perhaps have some error)
            if not file_size:
                file_size = world_utils.SECTOR_BYTES * 2
                fp.truncate(file_size)

            # read the file and populate the internal database
            # self._file_size = file_size

            fp.seek(0)

            # offsets = fp.read(world_utils.SECTOR_BYTES)
            # mod_times = fp.read(world_utils.SECTOR_BYTES)

            # self._free_sectors = free_sectors = numpy.full(
            #     file_size // world_utils.SECTOR_BYTES, True, bool
            # )
            # self._free_sectors[0:2] = False, False

            offsets = numpy.fromfile(
                fp, dtype=">u4", count=1024
            )
            mod_times = numpy.fromfile(
                fp, dtype=">u4", count=1024
            )

            # for offset in offsets:
            #     sector = offset >> 8
            #     count = offset & 0xFF
            #
            #     for i in range(sector, sector + count):
            #         if i >= len(free_sectors):
            #             return False
            #
            #         free_sectors[i] = False

            for x in range(32):
                for z in range(32):
                    offset = offsets[x + 32 * z]
                    if offset == 0:
                        continue
                    sector = offset >> 8
                    # count = offset & 0xFF   # the number of sectors used
                    fp.seek(world_utils.SECTOR_BYTES * sector)
                    # read int value and then read that amount of data
                    buffer_size = struct.unpack('>I', fp.read(4))[0]
                    self._chunks[(x, z)] = (False, mod_times[x + 32 * z], buffer_size, fp.read(buffer_size))

    def save(self):
        if self._dirty:
            offsets = numpy.zeros(1024, dtype=">u4")
            mod_times = numpy.zeros(1024, dtype=">u4")
            offset = 2
            data = []
            for (cx, cz), (dirty, mod_time, buffer_size, buffer) in self._chunks.items():
                index = cx + (cz << 5)
                sector_count = ((buffer_size + 4 | 0xFFF) + 1) >> 12
                offsets[index] = (offset << 8) + sector_count
                mod_times[index] = mod_time
                data.append(struct.pack('>I', buffer_size) + buffer + b'\x00' * ((sector_count << 12) - buffer_size - 4))
                offset += sector_count
            with open(self._file_path, 'wb') as fp:
                fp.write(struct.pack('>1024I', *offsets))    # there is probably a prettier way of doing this
                fp.write(struct.pack('>1024I', *mod_times))  # but I could not work it out with Numpy
                fp.write(b''.join(data))

    def get_chunk_data(self, cx: int, cz: int) -> nbt.NBTFile:
        if (cx, cz) in self._chunks:
            return self._decompress(self._chunks[(cx, cz)][3])
        else:
            raise ChunkDoesNotExist

    def put_chunk_data(self, cx: int, cz: int, data: nbt.NBTFile):
        """compress the data and put it in the class database"""
        self._dirty = True
        buffer_size, bytes_data = self._compress(data)
        self._chunks[(cx, cz)] = (True, int(time.time()), buffer_size, bytes_data)

    def delete_chunk_data(self, cx: int, cz: int):
        if (cx, cz) in self._chunks:
            del self._chunks[(cx, cz)]

    @staticmethod
    def _compress(data: nbt.NBTFile) -> Tuple[int, bytes]:
        """Convert an NBTFile into a compressed bytes object"""
        data = data.save_to(compressed=False)
        data = b'\x02' + zlib.compress(data)
        return len(data), data

    @staticmethod
    def _decompress(data: bytes) -> nbt.NBTFile:
        """Convert a bytes object into an NBTFile"""
        if data[0] == world_utils.VERSION_GZIP:
            return nbt.load(buffer=gzip.decompress(data[1:]), compressed=False)
        elif data[0] == world_utils.VERSION_DEFLATE:
            return nbt.load(buffer=zlib.decompress(data[1:]), compressed=False)
        raise Exception(f'Invalid compression type {data[0]}')


class AnvilRegionManager:
    def __init__(self, directory: str):
        self._directory = directory
        self._loaded_regions: Dict[Tuple[int, int], AnvilRegion] = {}

    # TODO: allow loading and saving to different dimensions

    def save(self):
        # use put_chunk_data to actually upload modified chunks
        # run this to push those changes to disk

        for region in self._loaded_regions.values():
            region.save()
            # TODO: perhaps delete the region from loaded regions so that memory usage doesn't explode

    def close(self):
        raise NotImplementedError
        # any final closing requirements (I don't think there are any for anvil)

    def get_chunk_data(self, cx: int, cz: int) -> nbt.NBTFile:
        """Get an NBTFile of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
        # get the region key
        return self._get_region(cx, cz).get_chunk_data(cx & 0x1F, cz & 0x1F)

    def _get_region(self, cx: int, cz: int, create=False) -> AnvilRegion:
        key = rx, rz = world_utils.chunk_coords_to_region_coords(cx, cz)
        if key in self._loaded_regions:
            return self._loaded_regions[key]

        # check the file exists and then open it
        file_path = os.path.join(self._directory, "region", f'r.{rx}.{rz}.mca')
        if os.path.exists(file_path):
            self._loaded_regions[key] = AnvilRegion(file_path)
        else:
            if create:
                self._loaded_regions[key] = AnvilRegion(file_path, True)
            else:
                raise ChunkDoesNotExist

        return self._loaded_regions[key]

    def put_chunk_data(self, cx: int, cz: int, data: nbt.NBTFile):
        """pass data to the region file class"""
        # get the region key
        self._get_region(cx, cz, create=True).put_chunk_data(cx & 0x1F, cz & 0x1F, data)

    def delete_chunk(self, cx: int, cz: int):
        try:
            self._get_region(cx, cz).delete_chunk_data(cx & 0x1F, cz & 0x1F)
        except ChunkDoesNotExist:
            pass


class AnvilFormat(Format):
    def __init__(self, directory: str):
        super().__init__(directory)
        self.root_tag = nbt.load(filename=os.path.join(self._directory, "level.dat"))
        self._region_manager = AnvilRegionManager(self._directory)

    def save(self):
        self._region_manager.save()
        # TODO: save other world data

    def close(self):
        pass    # TODO: release lock file

    def _max_world_version(self) -> Tuple:
        return 'anvil', self.root_tag['Data']['DataVersion'].value

    def delete_chunk(self, cx: int, cz: int):
        self._region_manager.delete_chunk(cx, cz)

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any):
        """
        Actually stores the data from the interface to disk.
        """
        self._region_manager.put_chunk_data(cx, cz, data)

    def _get_raw_chunk_data(self, cx, cz) -> Any:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        return self._region_manager.get_chunk_data(cx, cz)

    def _get_interface_key(self, raw_chunk_data) -> Tuple[str, int]:
        return "anvil", raw_chunk_data["DataVersion"].value

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

if __name__ == '__main__':
    import sys

    world_path = sys.argv[1]
    world = AnvilRegionManager(world_path)
    chunk = world.get_chunk_data(0, 0)
    print(chunk)
    world.put_chunk_data(0, 0, chunk)
    world.save()

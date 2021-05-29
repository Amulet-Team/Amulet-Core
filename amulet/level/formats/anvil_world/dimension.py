from __future__ import annotations

import os
from typing import Dict, Iterable
import re

import amulet_nbt as nbt

from amulet.utils import world_utils
from amulet.api.errors import ChunkDoesNotExist
from amulet.api.data_types import (
    ChunkCoordinates,
    RegionCoordinates,
)
from .region import AnvilRegion

InternalDimension = str


class AnvilDimensionManager:
    level_regex = re.compile(r"DIM(?P<level>-?\d+)")

    def __init__(self, directory: str, mcc=False):
        self._directory = directory
        self._regions: Dict[RegionCoordinates, AnvilRegion] = {}
        self._mcc = mcc

        # shallow load all of the existing region classes
        region_dir = os.path.join(self._directory, "region")
        if os.path.isdir(region_dir):
            for region_file_name in os.listdir(region_dir):
                rx, rz = AnvilRegion.get_coords(region_file_name)
                if rx is None:
                    continue
                self._regions[(rx, rz)] = AnvilRegion(
                    os.path.join(self._directory, "region", region_file_name),
                    mcc=self._mcc,
                )

    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        for region in self._regions.values():
            yield from region.all_chunk_coords()

    def has_chunk(self, cx: int, cz: int) -> bool:
        key = world_utils.chunk_coords_to_region_coords(cx, cz)
        return key in self._regions and self._regions[key].has_chunk(
            cx & 0x1F, cz & 0x1F
        )

    def save(self, unload=True):
        # use put_chunk_data to actually upload modified chunks
        # run this to push those changes to disk

        os.makedirs(self._directory, exist_ok=True)
        for region in self._regions.values():
            region.save()
            if unload:
                region.unload()

    def close(self):
        pass

    def unload(self):
        for region in self._regions.values():
            region.unload()

    def get_chunk_data(self, cx: int, cz: int) -> nbt.NBTFile:
        """Get an NBTFile of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
        # get the region key
        return self._get_region(cx, cz).get_chunk_data(cx & 0x1F, cz & 0x1F)

    def _get_region(self, cx: int, cz: int, create=False) -> AnvilRegion:
        key = rx, rz = world_utils.chunk_coords_to_region_coords(cx, cz)
        if key in self._regions:
            return self._regions[key]

        if create:
            file_path = os.path.join(self._directory, "region", f"r.{rx}.{rz}.mca")
            self._regions[key] = AnvilRegion(file_path, True, mcc=self._mcc)
        else:
            raise ChunkDoesNotExist

        return self._regions[key]

    def put_chunk_data(self, cx: int, cz: int, data: nbt.NBTFile):
        """pass data to the region file class"""
        # get the region key
        self._get_region(cx, cz, create=True).put_chunk_data(cx & 0x1F, cz & 0x1F, data)

    def delete_chunk(self, cx: int, cz: int):
        try:
            self._get_region(cx, cz).delete_chunk_data(cx & 0x1F, cz & 0x1F)
        except ChunkDoesNotExist:
            pass

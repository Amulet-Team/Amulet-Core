from __future__ import annotations

import os
from typing import Dict, Iterable
import re
import threading

from amulet_nbt import NamedTag

from amulet.utils import world_utils
from amulet.api.errors import ChunkDoesNotExist
from amulet.api.data_types import (
    ChunkCoordinates,
    RegionCoordinates,
)
from .region import AnvilRegionInterface

InternalDimension = str


ChunkDataType = Dict[str, NamedTag]


class AnvilDimensionManager:
    """
    A class to manage the data for a dimension.
    This can consist of multiple layers. Eg the region layer which contains chunk data and the entities layer which contains entities.
    """

    level_regex = re.compile(r"DIM(?P<level>-?\d+)")

    def __init__(self, directory: str, *, mcc=False, layers=("region",)):
        self._directory = directory
        self._mcc = mcc
        self.__layers: Dict[str, AnvilRegionManager] = {
            layer: AnvilRegionManager(
                os.path.join(self._directory, layer), mcc=self._mcc
            )
            for layer in layers
        }
        self.__default_layer = self.__layers[layers[0]]

    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        yield from self.__default_layer.all_chunk_coords()

    def has_chunk(self, cx: int, cz: int) -> bool:
        return self.__default_layer.has_chunk(cx, cz)

    def unload(self):
        for layer in self.__layers.values():
            layer.unload()

    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """
        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
        # get the region key
        return self.__default_layer.get_chunk_data(cx, cz)

    def get_chunk_data_layers(self, cx: int, cz: int) -> ChunkDataType:
        """Get the chunk data for each layer"""
        chunk_data = {}
        for layer_name, layer in self.__layers.items():
            try:
                chunk_data[layer_name] = layer.get_chunk_data(cx, cz)
            except ChunkDoesNotExist:
                pass

        if chunk_data:
            return chunk_data
        else:
            raise ChunkDoesNotExist

    def put_chunk_data(self, cx: int, cz: int, data: NamedTag):
        """pass data to the region file class"""
        self.__default_layer.put_chunk_data(cx, cz, data)

    def put_chunk_data_layers(self, cx: int, cz: int, data_layers: ChunkDataType):
        """Put one or more layers of data"""
        for layer_name, data in data_layers.items():
            if (
                layer_name not in self.__layers
                and layer_name.isalpha()
                and layer_name.islower()
            ):
                self.__layers[layer_name] = AnvilRegionManager(
                    os.path.join(self._directory, layer_name), mcc=self._mcc
                )
            if layer_name in self.__layers:
                self.__layers[layer_name].put_chunk_data(cx, cz, data)

    def delete_chunk(self, cx: int, cz: int):
        for layer in self.__layers.values():
            layer.delete_chunk(cx, cz)


class AnvilRegionManager:
    """A class to manage a directory of region files."""

    def __init__(self, directory: str, *, mcc=False):
        self._directory = directory
        self._regions: Dict[RegionCoordinates, AnvilRegionInterface] = {}
        self._mcc = mcc
        self._lock = threading.RLock()

    def unload(self):
        with self._lock:
            self._regions.clear()

    def _region_path(self, rx, rz) -> str:
        """Get the file path for a region file."""
        return os.path.join(self._directory, f"r.{rx}.{rz}.mca")

    def _has_region(self, rx: int, rz: int) -> bool:
        """Does a region file exist."""
        return os.path.isfile(self._region_path(rx, rz))

    def _get_region(self, rx: int, rz: int, create=False) -> AnvilRegionInterface:
        with self._lock:
            if (rx, rz) in self._regions:
                return self._regions[(rx, rz)]
            elif create or self._has_region(rx, rz):
                region = self._regions[(rx, rz)] = AnvilRegionInterface(
                    self._region_path(rx, rz), mcc=self._mcc
                )
                return region
            else:
                raise ChunkDoesNotExist

    def _iter_regions(self) -> Iterable[AnvilRegionInterface]:
        if os.path.isdir(self._directory):
            for region_file_name in os.listdir(self._directory):
                rx, rz = AnvilRegionInterface.get_coords(region_file_name)
                if rx is None:
                    continue
                yield self._get_region(rx, rz)

    def all_chunk_coords(self) -> Iterable[ChunkCoordinates]:
        for region in self._iter_regions():
            yield from region.all_chunk_coords()

    def has_chunk(self, cx: int, cz: int) -> bool:
        try:
            region = self._get_region(
                *world_utils.chunk_coords_to_region_coords(cx, cz)
            )
        except ChunkDoesNotExist:
            return False
        else:
            return region.has_chunk(cx & 0x1F, cz & 0x1F)

    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """
        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
        # get the region key
        return self._get_region(
            *world_utils.chunk_coords_to_region_coords(cx, cz)
        ).get_data(cx & 0x1F, cz & 0x1F)

    def put_chunk_data(self, cx: int, cz: int, data: NamedTag):
        """pass data to the region file class"""
        self._get_region(
            *world_utils.chunk_coords_to_region_coords(cx, cz), create=True
        ).write_data(cx & 0x1F, cz & 0x1F, data)

    def delete_chunk(self, cx: int, cz: int):
        try:
            region = self._get_region(
                *world_utils.chunk_coords_to_region_coords(cx, cz)
            )
        except ChunkDoesNotExist:
            pass
        else:
            region.delete_data(cx & 0x1F, cz & 0x1F)

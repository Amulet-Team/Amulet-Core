from __future__ import annotations

import os
from typing import Dict, Iterable
import re

from amulet_nbt import NamedTag

from amulet.utils import world_utils
from amulet.api.errors import ChunkDoesNotExist
from amulet.api.data_types import (
    ChunkCoordinates,
    RegionCoordinates,
)
from .region import AnvilRegion

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

    def save(self, unload=True):
        # use put_chunk_data to actually upload modified chunks
        # run this to push those changes to disk

        for layer in self.__layers.values():
            layer.save(unload)

    def close(self):
        pass

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
        self._regions: Dict[RegionCoordinates, AnvilRegion] = {}
        self._mcc = mcc

        # shallow load all of the existing region classes
        if os.path.isdir(self._directory):
            for region_file_name in os.listdir(self._directory):
                rx, rz = AnvilRegion.get_coords(region_file_name)
                if rx is None:
                    continue
                self._regions[(rx, rz)] = AnvilRegion(
                    os.path.join(self._directory, region_file_name),
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

    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """
        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
        # get the region key
        return self._get_region(cx, cz).get_chunk_data(cx & 0x1F, cz & 0x1F)

    def _get_region(self, cx: int, cz: int, create=False) -> AnvilRegion:
        key = rx, rz = world_utils.chunk_coords_to_region_coords(cx, cz)
        if key in self._regions:
            return self._regions[key]

        if create:
            file_path = os.path.join(self._directory, f"r.{rx}.{rz}.mca")
            self._regions[key] = AnvilRegion(file_path, True, mcc=self._mcc)
        else:
            raise ChunkDoesNotExist

        return self._regions[key]

    def put_chunk_data(self, cx: int, cz: int, data: NamedTag):
        """pass data to the region file class"""
        # get the region key
        self._get_region(cx, cz, create=True).put_chunk_data(cx & 0x1F, cz & 0x1F, data)

    def delete_chunk(self, cx: int, cz: int):
        try:
            self._get_region(cx, cz).delete_chunk_data(cx & 0x1F, cz & 0x1F)
        except ChunkDoesNotExist:
            pass

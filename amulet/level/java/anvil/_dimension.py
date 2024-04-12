from __future__ import annotations

from typing import TypeAlias
import os
from collections.abc import Iterator, Sequence
import re
import threading

from amulet_nbt import NamedTag

from amulet.utils import world_utils
from amulet.errors import ChunkDoesNotExist
from amulet.api.data_types import (
    ChunkCoordinates,
    RegionCoordinates,
)
from ._region import AnvilRegion


ChunkDataType: TypeAlias = dict[str, NamedTag]


class AnvilDimensionLayer:
    """A class to manage a directory of region files."""

    def __init__(self, directory: str, *, mcc: bool = False):
        self._directory = directory
        self._regions: dict[RegionCoordinates, AnvilRegion] = {}
        self._mcc = mcc
        self._lock = threading.RLock()

    def _region_path(self, rx: int, rz: int) -> str:
        """Get the file path for a region file."""
        return os.path.join(self._directory, f"r.{rx}.{rz}.mca")

    def _has_region(self, rx: int, rz: int) -> bool:
        """Does a region file exist."""
        return os.path.isfile(self._region_path(rx, rz))

    def _get_region(self, rx: int, rz: int, create: bool = False) -> AnvilRegion:
        with self._lock:
            if (rx, rz) in self._regions:
                return self._regions[(rx, rz)]
            elif create or self._has_region(rx, rz):
                region = self._regions[(rx, rz)] = AnvilRegion(
                    self._region_path(rx, rz), mcc=self._mcc
                )
                return region
            else:
                raise ChunkDoesNotExist

    def _iter_regions(self) -> Iterator[AnvilRegion]:
        if os.path.isdir(self._directory):
            for region_file_name in os.listdir(self._directory):
                try:
                    rx, rz = AnvilRegion.get_coords(region_file_name)
                except ValueError:
                    continue
                else:
                    yield self._get_region(rx, rz)

    def all_chunk_coords(self) -> Iterator[ChunkCoordinates]:
        for region in self._iter_regions():
            yield from region.all_coords()

    def has_chunk(self, cx: int, cz: int) -> bool:
        try:
            region = self._get_region(
                *world_utils.chunk_coords_to_region_coords(cx, cz)
            )
        except ChunkDoesNotExist:
            return False
        else:
            return region.has_data(cx, cz)

    def get_chunk_data(self, cx: int, cz: int) -> NamedTag:
        """
        Get a NamedTag of a chunk from the database.
        Will raise ChunkDoesNotExist if the region or chunk does not exist
        """
        # get the region key
        return self._get_region(
            *world_utils.chunk_coords_to_region_coords(cx, cz)
        ).get_data(cx, cz)

    def put_chunk_data(self, cx: int, cz: int, data: NamedTag) -> None:
        """pass data to the region file class"""
        self._get_region(
            *world_utils.chunk_coords_to_region_coords(cx, cz), create=True
        ).set_data(cx, cz, data)

    def delete_chunk(self, cx: int, cz: int) -> None:
        try:
            region = self._get_region(
                *world_utils.chunk_coords_to_region_coords(cx, cz)
            )
        except ChunkDoesNotExist:
            pass
        else:
            region.delete_data(cx, cz)

    def compact(self) -> None:
        """Compact all region files in this layer"""
        for region in self._iter_regions():
            region.compact()


class AnvilDimension:
    """
    A class to manage the data for a dimension.
    This can consist of multiple layers. Eg the region layer which contains chunk data and the entities layer which contains entities.
    """

    level_regex = re.compile(r"DIM(?P<level>-?\d+)")

    def __init__(
        self, directory: str, *, mcc: bool = False, layers: Sequence[str] = ("region",)
    ) -> None:
        self._directory = directory
        self._mcc = mcc
        self.__layers: dict[str, AnvilDimensionLayer] = {
            layer: AnvilDimensionLayer(
                os.path.join(self._directory, layer), mcc=self._mcc
            )
            for layer in layers
        }
        self.__default_layer = self.__layers[layers[0]]

    def all_chunk_coords(self) -> Iterator[ChunkCoordinates]:
        yield from self.__default_layer.all_chunk_coords()

    def has_chunk(self, cx: int, cz: int) -> bool:
        return self.__default_layer.has_chunk(cx, cz)

    def get_chunk_data(self, cx: int, cz: int) -> ChunkDataType:
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

    def put_chunk_data(
        self, cx: int, cz: int, data_layers: ChunkDataType
    ) -> None:
        """Put one or more layers of data"""
        for layer_name, data in data_layers.items():
            if (
                layer_name not in self.__layers
                and layer_name.isalpha()
                and layer_name.islower()
            ):
                self.__layers[layer_name] = AnvilDimensionLayer(
                    os.path.join(self._directory, layer_name), mcc=self._mcc
                )
            if layer_name in self.__layers:
                self.__layers[layer_name].put_chunk_data(cx, cz, data)

    def delete_chunk(self, cx: int, cz: int) -> None:
        for layer in self.__layers.values():
            layer.delete_chunk(cx, cz)

    def compact(self) -> None:
        """Compact all region files in this dimension"""
        for layer in self.__layers.values():
            layer.compact()
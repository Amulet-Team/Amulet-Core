from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Tuple
import numpy
from .. import selection

from amulet.api.data_types import (
    CoordinatesAny,
    ChunkCoordinates,
    SubChunkCoordinates,
    FloatTriplet,
    BlockCoordinates,
)


class AbstractBaseSelection(ABC):
    __slots__ = ()

    @abstractmethod
    def __contains__(self, item: CoordinatesAny) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def blocks(self) -> Iterable[BlockCoordinates]:
        raise NotImplementedError

    @property
    @abstractmethod
    def bounds(self) -> Tuple[BlockCoordinates, BlockCoordinates]:
        raise NotImplementedError

    @property
    @abstractmethod
    def bounds_array(self) -> numpy.ndarray:
        raise NotImplementedError

    @abstractmethod
    def chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterable[Tuple[ChunkCoordinates, selection.box.SelectionBox]]:
        raise NotImplementedError

    @abstractmethod
    def chunk_count(self, sub_chunk_size: int = 16) -> int:
        raise NotImplementedError

    @abstractmethod
    def chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Iterable[ChunkCoordinates]:
        raise NotImplementedError

    @abstractmethod
    def contains_block(self, coords: CoordinatesAny) -> bool:
        raise NotImplementedError

    # @abstractmethod
    # def contains_box(self, other: box.SelectionBox) -> bool:
    #     raise NotImplementedError

    @abstractmethod
    def contains_point(self, coords: CoordinatesAny) -> bool:
        raise NotImplementedError

    @abstractmethod
    def intersection(self, other):
        raise NotImplementedError

    @abstractmethod
    def intersects(self, other) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def max(self) -> BlockCoordinates:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_array(self) -> numpy.ndarray:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_x(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_y(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_z(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def min(self) -> BlockCoordinates:
        raise NotImplementedError

    @property
    @abstractmethod
    def min_array(self) -> numpy.ndarray:
        raise NotImplementedError

    @property
    @abstractmethod
    def min_x(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def min_y(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def min_z(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def sub_chunk_boxes(
        self, sub_chunk_size: int = 16
    ) -> Iterable[Tuple[SubChunkCoordinates, selection.box.SelectionBox]]:
        raise NotImplementedError

    @abstractmethod
    def sub_chunk_count(self, sub_chunk_size: int = 16) -> int:
        raise NotImplementedError

    @abstractmethod
    def sub_chunk_locations(
        self, sub_chunk_size: int = 16
    ) -> Iterable[SubChunkCoordinates]:
        raise NotImplementedError

    @abstractmethod
    def subtract(self, other):
        raise NotImplementedError

    @abstractmethod
    def transform(
        self, scale: FloatTriplet, rotation: FloatTriplet, translation: FloatTriplet
    ):
        raise NotImplementedError

    @property
    @abstractmethod
    def volume(self) -> int:
        raise NotImplementedError

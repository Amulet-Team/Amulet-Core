import numpy
from typing import Tuple, Union

FloatTriplet = Tuple[float, float, float]
Dimension = str
DimensionID = str
RegionCoordinates = Tuple[int, int]
ChunkCoordinates = Tuple[int, int]
SubChunkCoordinates = Tuple[int, int, int]
DimensionCoordinates = Tuple[Dimension, int, int]
BlockCoordinates = Tuple[int, int, int]
BlockCoordinatesNDArray = numpy.ndarray
BlockCoordinatesAny = Union[BlockCoordinates, BlockCoordinatesNDArray]
PointCoordinates = FloatTriplet
PointCoordinatesNDArray = numpy.ndarray
PointCoordinatesAny = Union[PointCoordinates, PointCoordinatesNDArray]
CoordinatesAny = Union[BlockCoordinatesAny, PointCoordinatesAny]
SubChunkNDArray = numpy.ndarray
BiomeType = str

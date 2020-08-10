from typing import Union, Tuple
import numpy

# from nptyping import NDArray

FloatTriplet = Tuple[float, float, float]

Dimension = str
RegionCoordinates = Tuple[int, int]
ChunkCoordinates = Tuple[int, int]
SubChunkCoordinates = Tuple[int, int, int]
DimensionCoordinates = Tuple[Dimension, int, int]

BlockCoordinates = Tuple[int, int, int]
BlockCoordinatesNDArray = numpy.ndarray  # NDArray[(3, ), numpy.int]
BlockCoordinatesAny = Union[BlockCoordinates, BlockCoordinatesNDArray]
PointCoordinates = FloatTriplet
PointCoordinatesNDArray = numpy.ndarray  # NDArray[(3, ), numpy.float]
PointCoordinatesAny = Union[PointCoordinates, PointCoordinatesNDArray]
CoordinatesAny = Union[BlockCoordinatesAny, PointCoordinatesAny]

SubChunkNDArray = numpy.ndarray  # NDArray[(16, 16, 16), numpy.uint]

BiomeType = str

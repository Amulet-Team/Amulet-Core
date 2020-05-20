from typing import Union, Tuple
import numpy
# from nptyping import NDArray

Dimension = str
RegionCoordinates = Tuple[int, int]
ChunkCoordinates = Tuple[int, int]
SubChunkCoordinates = Tuple[int, int, int]
DimensionCoordinates = Tuple[Dimension, int, int]

BlockCoordinates = Tuple[int, int, int]
BlockCoordinatesNDArray = numpy.ndarray  # NDArray[(3, ), numpy.int]
BlockCoordinatesAny = Union[BlockCoordinates, BlockCoordinatesNDArray]
PointCoordinates = Tuple[float, float, float]
PointCoordinatesNDArray = numpy.ndarray  # NDArray[(3, ), numpy.float]
PointCoordinatesAny = Union[PointCoordinates, PointCoordinatesNDArray]
CoordinatesAny = Union[BlockCoordinatesAny, PointCoordinatesAny]

SubChunkNDArray = numpy.ndarray  # NDArray[(16, 16, 16), numpy.uint]
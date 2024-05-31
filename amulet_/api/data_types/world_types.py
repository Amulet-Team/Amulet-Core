from typing import Union, TypeAlias
import numpy

# from nptyping import NDArray


#: The data type for the dimension identifier.
Dimension: TypeAlias = str
DimensionID: TypeAlias = str


#: The data type for the dimension and x and z coordinates of a chunk within a world. Note these are no the same as block coordinates.
DimensionCoordinates: TypeAlias = tuple[Dimension, int, int]


#: The data type for the x, y and z location of a block within the world in the form of a numpy array.
BlockCoordinatesNDArray: TypeAlias = numpy.ndarray  # NDArray[(3, ), int]

#: The data type for the x, y and z location of a block within the world in either tuple or numpy array form.
BlockCoordinatesAny: TypeAlias = Union[BlockCoordinates, BlockCoordinatesNDArray]


#: The data type for the x, y and z location of a point within the world in the form of a numpy array.
PointCoordinatesNDArray: TypeAlias = numpy.ndarray  # NDArray[(3, ), numpy.float]

#: The data type for the x, y and z location of a point within the world in either tuple or numpy array form.
PointCoordinatesAny: TypeAlias = Union[PointCoordinates, PointCoordinatesNDArray]

#: The data type for x, y and z location in either float or int and tuple or numpy array format.
CoordinatesAny: TypeAlias = Union[BlockCoordinatesAny, PointCoordinatesAny]

#: The data type for a sub-chunk array. This array should be a 16x16x16 numpy array.
SubChunkNDArray: TypeAlias = numpy.ndarray  # NDArray[(16, 16, 16), numpy.uint32]

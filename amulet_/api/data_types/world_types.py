from typing import Union, TypeAlias
import numpy

# from nptyping import NDArray


#: The data type for the dimension identifier.
Dimension: TypeAlias = str
DimensionID: TypeAlias = str


#: The data type for the dimension and x and z coordinates of a chunk within a world. Note these are no the same as block coordinates.
DimensionCoordinates: TypeAlias = tuple[Dimension, int, int]

#: The data type for a sub-chunk array. This array should be a 16x16x16 numpy array.
SubChunkNDArray: TypeAlias = numpy.ndarray  # NDArray[(16, 16, 16), numpy.uint32]

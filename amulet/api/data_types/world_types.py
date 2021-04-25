from typing import Union, Tuple
import numpy

# from nptyping import NDArray

#: The data type for a Tuple containing three floats. Use :data:`PointCoordinates` for x, y, z float coordinates.
FloatTriplet = Tuple[float, float, float]

#: The data type for the dimension identifier.
Dimension = str

#: The data type for the x and z coordinates of a region file. Note these are no the same as block coordinates.
RegionCoordinates = Tuple[int, int]

#: The data type for the x and z coordinate of a chunk. Note these are no the same as block coordinates.
ChunkCoordinates = Tuple[int, int]

#: The data type for the x, y and z coordinates of a sub-chunk within the world. Note these are no the same as block coordinates.
SubChunkCoordinates = Tuple[int, int, int]

#: The data type for the dimension and x and z coordinates of a chunk within a world. Note these are no the same as block coordinates.
DimensionCoordinates = Tuple[Dimension, int, int]

#: The data type for the x, y and z location of a block within the world.
BlockCoordinates = Tuple[int, int, int]

#: The data type for the x, y and z location of a block within the world in the form of a numpy array.
BlockCoordinatesNDArray = numpy.ndarray  # NDArray[(3, ), int]

#: The data type for the x, y and z location of a block within the world in either tuple or numpy array form.
BlockCoordinatesAny = Union[BlockCoordinates, BlockCoordinatesNDArray]

#: The data type for the x, y and z location of a point within the world.
PointCoordinates = FloatTriplet

#: The data type for the x, y and z location of a point within the world in the form of a numpy array.
PointCoordinatesNDArray = numpy.ndarray  # NDArray[(3, ), numpy.float]

#: The data type for the x, y and z location of a point within the world in either tuple or numpy array form.
PointCoordinatesAny = Union[PointCoordinates, PointCoordinatesNDArray]

#: The data type for x, y and z location in either float or int and tuple or numpy array format.
CoordinatesAny = Union[BlockCoordinatesAny, PointCoordinatesAny]

#: The data type for a sub-chunk array. This array should be a 16x16x16 numpy array.
SubChunkNDArray = numpy.ndarray  # NDArray[(16, 16, 16), numpy.uint32]

#: The data type for a biome string identifier.
BiomeType = str

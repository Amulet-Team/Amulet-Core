from typing import Union, Tuple, TypeAlias
import numpy

# from nptyping import NDArray

#: The data type for a Tuple containing three floats. Use :data:`PointCoordinates` for x, y, z float coordinates.
FloatTriplet: TypeAlias = Tuple[float, float, float]

#: The data type for the dimension identifier.
Dimension: TypeAlias = str
DimensionID: TypeAlias = str

#: The data type for the x and z coordinates of a region file. Note these are no the same as block coordinates.
RegionCoordinates: TypeAlias = Tuple[int, int]

#: The data type for the x and z coordinate of a chunk. Note these are no the same as block coordinates.
ChunkCoordinates: TypeAlias = Tuple[int, int]

#: The data type for the x, y and z coordinates of a sub-chunk within the world. Note these are no the same as block coordinates.
SubChunkCoordinates: TypeAlias = Tuple[int, int, int]

#: The data type for the dimension and x and z coordinates of a chunk within a world. Note these are no the same as block coordinates.
DimensionCoordinates: TypeAlias = Tuple[Dimension, int, int]

#: The data type for the x, y and z location of a block within the world.
BlockCoordinates: TypeAlias = Tuple[int, int, int]

#: The data type for the x, y and z location of a block within the world in the form of a numpy array.
BlockCoordinatesNDArray: TypeAlias = numpy.ndarray  # NDArray[(3, ), int]

#: The data type for the x, y and z location of a block within the world in either tuple or numpy array form.
BlockCoordinatesAny: TypeAlias = Union[BlockCoordinates, BlockCoordinatesNDArray]

#: The data type for the x, y and z location of a point within the world.
PointCoordinates: TypeAlias = FloatTriplet

#: The data type for the x, y and z location of a point within the world in the form of a numpy array.
PointCoordinatesNDArray: TypeAlias = numpy.ndarray  # NDArray[(3, ), numpy.float]

#: The data type for the x, y and z location of a point within the world in either tuple or numpy array form.
PointCoordinatesAny: TypeAlias = Union[PointCoordinates, PointCoordinatesNDArray]

#: The data type for x, y and z location in either float or int and tuple or numpy array format.
CoordinatesAny: TypeAlias = Union[BlockCoordinatesAny, PointCoordinatesAny]

#: The data type for a sub-chunk array. This array should be a 16x16x16 numpy array.
SubChunkNDArray: TypeAlias = numpy.ndarray  # NDArray[(16, 16, 16), numpy.uint32]

#: The data type for a biome string identifier.
BiomeType: TypeAlias = str

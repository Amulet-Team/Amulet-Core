from typing import TypeAlias
import numpy

#: The type for a dimension identifier
DimensionId: TypeAlias = str

#: The data type for the x and z coordinates of a region file. Note these are no the same as block coordinates.
RegionCoordinates: TypeAlias = tuple[int, int]

#: The data type for the x and z coordinate of a chunk. Note these are no the same as block coordinates.
ChunkCoordinates: TypeAlias = tuple[int, int]

#: The data type for the x, y and z coordinates of a sub-chunk within the world. Note these are no the same as block coordinates.
SubChunkCoordinates: TypeAlias = tuple[int, int, int]

#: The data type for the x, y and z location of a block within the world.
BlockCoordinates: TypeAlias = tuple[int, int, int]

#: The data type for the x, y and z location of a block within the world in the form of a numpy array.
BlockCoordinatesArray: TypeAlias = numpy.ndarray  # NDArray[(3, ), int]

#: The data type for the x, y and z location of a point within the world.
PointCoordinates: TypeAlias = tuple[float, float, float]

#: The data type for the x, y and z location of a point within the world in the form of a numpy array.
PointCoordinatesArray: TypeAlias = numpy.ndarray  # NDArray[(3, ), numpy.float]

#: The data type for a tuple containing three floats. Use :data:`PointCoordinates` for x, y, z float coordinates.
FloatTriplet: TypeAlias = tuple[float, float, float]

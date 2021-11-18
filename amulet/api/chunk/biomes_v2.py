"""
This needs to store biome data in many different shapes and facilitate switching between them.
Current known states (more could be added)
2D (one array per chunk)
16x16 - old chunks

3D (one array per sub-chunk)
1 - one value per sub-chunk (if all values in the array are the same)
4x4x4 - java
16x16x16 - bedrock
8x1x8 - cubic chunks

These are all powers of 2 which makes things a bit nicer.
I think we can assume this will always be the case.
"""

from typing import Tuple, Union, Dict, Optional
import numpy
from enum import IntEnum

Shape2D = Tuple[int, int]
Shape3D = Tuple[int, int, int]
ValidShapes = {2 ** i for i in range(1, 5)}


class BiomesShape(IntEnum):
    """
    An enum of the different states the :class:`Biomes` class can be in.

    >>> ShapeNull = 0  # The biome array does not exist
    >>> Shape2D = 2  # The biome array is a 2D array
    >>> Shape3D = 3  # The biome array is a 3D array
    """

    ShapeNull = 0  # doc: The biome array does not exist
    Shape2D = 2  # doc: The biome array is a 2D array
    Shape3D = 3  # doc: The biome array is a 3D array


def validate_shape(shape: Tuple[int], ndim: int):
    if not (len(shape) == 3 and all(s in ValidShapes for s in shape)):
        raise ValueError(f"Array must be {ndim}D array with power of 2 sizes.")


def validate_data(data: Union[int, numpy.ndarray], ndim: int) -> numpy.ndarray:
    if isinstance(data, int):
        data = numpy.array(data).reshape((1, 1, 1))
    if not isinstance(data, numpy.ndarray):
        raise TypeError(f"{ndim}D data must be a numpy array.")
    validate_shape(data.shape, ndim)
    return data


class BiomeData:
    default_biome: int
    ndim: BiomesShape
    biome_2d: Optional[numpy.ndarray]
    biome_3d: Dict[int, Union[numpy.ndarray]]

    def __init__(
        self,
        raw_data: Union[None, numpy.ndarray, Dict[int, Union[int, numpy.ndarray]]],
        default_biome: int,
    ):
        self.ndim = BiomesShape.ShapeNull
        self.biome_2d = None
        self.biome_3d = {}
        self.default_biome = default_biome

        if raw_data is None:
            pass
        elif isinstance(raw_data, numpy.ndarray):
            validate_data(raw_data, 2)
            self.biome_2d = raw_data.astype(numpy.uint32)
            self.ndim = BiomesShape.Shape2D
        elif isinstance(raw_data, dict):
            for k, v in raw_data:
                if not isinstance(k, int):
                    raise TypeError("Keys must be ints.")
                self.biome_3d[k] = validate_data(v, 3)
            self.ndim = BiomesShape.Shape3D
        else:
            raise ValueError(f"Unsupported type {type(raw_data)}")

    def convert(self, shape: BiomesShape):
        """
        Convert from one shape to another.
        Set the dimension number.
        If going between 2D and 3D do a conversion step.

        :param shape: The new BiomeShape
        """
        if self.ndim is not shape:
            if not isinstance(shape, BiomesShape):
                raise TypeError("Shape must be a value of BiomeShape")
            if shape is BiomesShape.Shape2D:
                if self.ndim is BiomesShape.Shape3D:
                    # todo: convert from 2D to 3D. Replace the 2D array with the data from the 3D data.
                    pass
            elif shape is BiomesShape.Shape3D:
                if self.ndim is BiomesShape.Shape2D:
                    # todo: Convert from 2D to 3D. Replace the 3D array with the data from the 2D data.
                    pass
            self.ndim = shape


class BaseBiome:
    # These are private variables. Do not use them.
    _biome_data: BiomeData
    _ndim = 0
    _shape: Tuple[int, ...]

    def __init__(self, biome_data: BiomeData, shape: Tuple[int, ...]):
        self._biome_data = biome_data
        shape = tuple(shape)
        validate_shape(shape, self._ndim)
        self._shape = shape


class Biome2D(BaseBiome):
    """Represents a 2D array storing biomes for a vertical column."""

    _ndim = 2
    _shape: Shape2D

    def __init__(self, biome_data: BiomeData, shape: Shape2D):
        super().__init__(biome_data, shape)

    @property
    def shape(self) -> Shape2D:
        """The shape the array data has been requested in."""
        return self._shape

    # def _populate_2d(self):
    #     if self._biome_data.biome_2d is None:
    #         # populate from 3D biomes
    #         if self._biome_data.biome_3d:
    #             _, arr3d = next(sorted(self._biome_data.biome_3d.items(), key=lambda x: x[0]))
    #         else:
    #             self._biome_data.biome_2d = numpy.full(self._shape, self._biome_data.default_biome)

    @property
    def array(self) -> numpy.ndarray:
        """Get the 2D array for this chunk."""
        self._biome_data.ndim = BiomesShape.Shape2D
        # TODO
        raise NotImplementedError


class Biome3D(BaseBiome):
    """Represents all 3D arrays in a chunk."""

    _ndim = 3
    _shape: Shape3D

    def __init__(self, biome_data: BiomeData, shape: Shape3D):
        super().__init__(biome_data, shape)

    @property
    def shape(self) -> Shape3D:
        """The shape the array data has been requested in."""
        return self._shape

    def get_raw(self, cy: int) -> numpy.ndarray:
        """
        Get the raw data for a given sub-chunk.
        This will not modify the data stored.

        :param cy: The sub-chunk index to get.
        :return: The raw array as it is stored.
        :raises KeyError if the requested item is not present.
        """
        return self._biome_data.biome_3d[cy]

    def get_array(self, cy: int) -> numpy.ndarray:
        """
        Get the array for a given sub-chunk with the requested shape.
        This will resize the stored array, potentially adding or destroying data that previously existed.

        :param cy: The sub-chunk index to get.
        :return: Numpy array resized to match :attr:`shape`
        :raises KeyError if the requested item is not present.
        """
        # TODO
        raise NotImplementedError

    def view_array(self, cy: int) -> numpy.ndarray:
        """
        Get the array for a given sub-chunk with the requested shape.
        This will create a resized copy without modifying the internal state.

        :param cy: The sub-chunk index to get.
        :return: Numpy array resized to match :attr:`shape`
        :raises KeyError if the requested item is not present.
        """
        # TODO
        raise NotImplementedError

    def set_array(self, cy: int, value: Union[int, numpy.ndarray]):
        """
        Set the array for a given sub-chunk.

        :param cy: The sub-chunk index to set.
        :param value: The array or value to set.
        """
        self._biome_data.biome_3d[cy] = validate_data(value, 3)

    def __contains__(self, cy: int):
        """Check if an array is defined for a given sub-chunk.

        >>> 5 in biome_3d

        :param cy: The sub-chunk index to check.
        :return: True if the key is populated. False otherwise.
        """
        return cy in self._biome_data.biome_3d

    def __iter__(self):
        """Iterate through all sub-chunk indexes that are defined in the data."""
        yield from self._biome_data.biome_3d


class Biomes:
    def __init__(self, *args, **kwargs):
        self.__biome_data = BiomeData(*args, **kwargs)

    def as_2d(self, shape: Shape2D = (16, 16)) -> Biome2D:
        return Biome2D(self.__biome_data, shape)

    def as_3d(self, shape: Shape3D = (16, 16, 16)) -> Biome3D:
        return Biome3D(self.__biome_data, shape)

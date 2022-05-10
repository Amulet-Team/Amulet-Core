import numpy
from typing import Union, Optional, Dict, Tuple
from copy import deepcopy
from enum import IntEnum


from amulet.api.partial_3d_array import UnboundedPartial3DArray


class Biomes3D(UnboundedPartial3DArray):
    """
    The Biomes3D class is designed to represent a 3D integer array but with no vertical height limit.

    See :class:`UnboundedPartial3DArray` for more information on how this works.
    """

    def __init__(
        self,
        input_array: Optional[Union[Dict[int, numpy.ndarray], "Biomes3D"]] = None,
    ):
        """
        Construct a :class:`Biomes3D` class from the given data.

        :param input_array: Either an instance of :class:`Biomes3D` or a dictionary converting sub-chunk id to a 4x4x4 numpy array.
        """
        if input_array is None:
            input_array = {}
        if isinstance(input_array, Biomes3D):
            input_array: dict = deepcopy(input_array._sections)
        if not isinstance(input_array, dict):
            raise Exception(f"Input array must be Biomes3D or dict, got {input_array}")
        super().__init__(numpy.uint32, 0, (4, 4, 4), (0, 16), sections=input_array)


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


class Biomes:
    """
    Biomes is a class used to store a 2D biome array and/or 3D biome array and facilitate switching between them.

    There are three states biomes can be in.

    The first is a blank state where no biomes are defined. This is used when a chunk is partially generated and the biomes array has not be created.

    The second is a 2D array of size (16, 16) used for old Java worlds and Bedrock worlds.

    The last is the 3D state used since Java 1.15. See :class:`Biomes3D` for more information.
    """

    __slots__ = ("_2d", "_3d", "_dimension")
    _2d: Optional[numpy.ndarray]
    _3d: Optional[Biomes3D]
    _dimension: BiomesShape

    def __init__(
        self, array: Union[numpy.ndarray, Biomes3D, Dict[int, numpy.ndarray]] = None
    ):
        """
        Construct a new instance of :class:`Biomes`

        :param array: The array to initialise with. Can be None or not defined to have the empty state.
        """
        self._2d: Optional[numpy.ndarray] = None
        self._3d: Optional[Biomes3D] = None
        if array is None:
            self._dimension = BiomesShape.ShapeNull
        elif isinstance(array, numpy.ndarray):
            assert array.shape == (
                16,
                16,
            ), "If Biomes is given an ndarray it must be 16x16"
            self._2d = array.copy()
            self._dimension = BiomesShape.Shape2D
        elif isinstance(array, (dict, Biomes3D)):
            self._3d = Biomes3D(array)
            self._dimension = BiomesShape.Shape3D

    def to_raw(
        self,
    ) -> Tuple[
        BiomesShape, Optional[numpy.ndarray], Optional[Dict[int, numpy.ndarray]]
    ]:
        """Don't use this method. Use to pickle data."""
        if self._3d is None:
            sections = None
        else:
            sections = self._3d._sections
        return self._dimension, self._2d, sections

    @classmethod
    def from_raw(
        cls,
        dimension: BiomesShape,
        d2: Optional[numpy.ndarray],
        d3: Optional[Dict[int, numpy.ndarray]],
    ) -> "Biomes":
        """Don't use this method. Use to unpickle data."""
        biomes = cls()
        biomes._dimension = dimension
        biomes._2d = d2
        if d3 is not None:
            biomes._3d = Biomes3D(d3)
        return biomes

    @property
    def dimension(self) -> BiomesShape:
        """
        The number of dimensions the data has

        :attr:`BiomesShape.ShapeNull` when there is no data.
        Will error if you try accessing data from it without converting to one of the other formats.

        :attr:`BiomesShape.Shape2D` when the data is a 2D (16, 16) numpy array.

        :attr:`BiomesShape.Shape3D` when the data is a 3D (4, inf, 4) :class:`Biome3D` array made of sections of size (4, 4, 4)."""
        return self._dimension

    def convert_to_2d(self):
        """
        Convert the data to the 2D 16x16 format from whatever format it was in.

        If it was in the Null state it will be initialised with the first entry in the :obj:`~amulet.api.registry.biome_manager.BiomeManager`.

        In this mode this class will behave like a numpy array.
        """
        if self._2d is None:
            self._2d = numpy.zeros((16, 16), numpy.uint32)
        if self._dimension != BiomesShape.Shape2D:
            if self._dimension == BiomesShape.Shape3D and self._3d is not None:
                # convert from 3D
                self._2d[:, :] = numpy.kron(
                    numpy.reshape(self._3d[:, 0, :], (4, 4)), numpy.ones((4, 4))
                )
            self._dimension = BiomesShape.Shape2D

    def convert_to_3d(self):
        """
        Convert the data to the 3D (4, inf, 4) format from whatever format it was in.

        If it was in the Null state it will be initialised with the first entry in the :class:`~amulet.api.registry.biome_manager.BiomeManager`.

        In this mode this class will behave like the :class:`Biome3D` class.
        """
        if self._3d is None:
            self._3d = Biomes3D()
        if self._dimension != BiomesShape.Shape3D:
            if self._dimension == BiomesShape.Shape2D and self._2d is not None:
                # convert from 2D
                self._3d[:, 0, :] = self._2d[::4, ::4].reshape(4, 1, 4)
            self._dimension = BiomesShape.Shape3D

    def _get_active(self) -> Union[numpy.ndarray, Biomes3D]:
        if self._dimension == BiomesShape.ShapeNull:
            raise Exception(
                "You are trying to use Biomes but have not picked a format. Use one of the convert methods to specify the format."
            )
        elif self._dimension == BiomesShape.Shape2D:
            self.convert_to_2d()
            return self._2d
        elif self._dimension == BiomesShape.Shape3D:
            self.convert_to_3d()
            return self._3d
        else:
            raise Exception("Dimension is invalid. This shouldn't happen")

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        for k in self.__slots__:
            setattr(result, k, getattr(self, k))
        return result

    def __deepcopy__(self, memodict=None):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k in self.__slots__:
            setattr(result, k, deepcopy(getattr(self, k), memodict))
        return result

    def __getattr__(self, item):
        return self._get_active().__getattribute__(item)

    def __contains__(self, item):
        return self._get_active().__contains__(item)

    def __getitem__(self, item):
        return self._get_active().__getitem__(item)

    def __setitem__(self, key, value):
        self._get_active().__setitem__(key, value)

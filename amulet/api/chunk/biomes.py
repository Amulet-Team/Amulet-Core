import numpy
from typing import Union, Optional, Dict, Tuple
from copy import deepcopy


from amulet.api.partial_3d_array import UnboundedPartial3DArray


class Biomes3D(UnboundedPartial3DArray):
    def __init__(
        self,
        input_array: Optional[Union[Dict[int, numpy.ndarray], "Biomes3D"]] = None,
    ):
        if input_array is None:
            input_array = {}
        if isinstance(input_array, Biomes3D):
            input_array: dict = deepcopy(input_array._sections)
        if not isinstance(input_array, dict):
            raise Exception(f"Input array must be Biomes3D or dict, got {input_array}")
        super().__init__(numpy.uint32, 0, (4, 4, 4), (0, 16), sections=input_array)


class Biomes:
    # __slots__ = ("_2d", "_3d", "_dimension")

    def __init__(
        self, array: Union[numpy.ndarray, Biomes3D, Dict[int, numpy.ndarray]] = None
    ):
        self._2d: Optional[numpy.ndarray] = None
        self._3d: Optional[Biomes3D] = None
        if array is None:
            self._dimension = 0
        elif isinstance(array, numpy.ndarray):
            assert array.shape == (
                16,
                16,
            ), "If Biomes is given an ndarray it must be 16x16"
            self._2d = array.copy()
            self._dimension = 2
        elif isinstance(array, (dict, Biomes3D)):
            self._3d = Biomes3D(array)
            self._dimension = 3

    def to_raw(
        self,
    ) -> Tuple[int, Optional[numpy.ndarray], Optional[Dict[int, numpy.ndarray]]]:
        """Don't use this method. Use to pickle data."""
        if self._3d is None:
            sections = None
        else:
            sections = self._3d._sections
        return self._dimension, self._2d, sections

    @classmethod
    def from_raw(
        cls,
        dimension: int,
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
    def dimension(self) -> int:
        """The number of dimensions the data has
        0 when there is no data. Will error if you try accessing data from it without converting to one of the other formats.
        2 when the data is a 2D 16x16 numpy array.
        3 when the data is a 3D 4xinfx4 Biome3D array made of sections of size 4x4x4."""
        return self._dimension

    def convert_to_2d(self):
        """Convert the data in whatever format it is in to the 2D 16x16 format."""
        if self._2d is None:
            self._2d = numpy.zeros((16, 16), numpy.uint32)
        if self._dimension != 2:
            if self._dimension == 3 and self._3d is not None:
                # convert from 3D
                self._2d[:, :] = numpy.kron(
                    numpy.reshape(self._3d[:, 0, :], (4, 4)), numpy.ones((4, 4))
                )
            self._dimension = 2

    def convert_to_3d(self):
        """Convert the data in whatever format it is in to the 3D 4xinfx4 format."""
        if self._3d is None:
            self._3d = Biomes3D()
        if self._dimension != 3:
            if self._dimension == 2 and self._2d is not None:
                # convert from 2D
                self._3d[:, 0, :] = self._2d[::4, ::4].reshape(4, 1, 4)
            self._dimension = 3

    def _get_active(self) -> Union[numpy.ndarray, Biomes3D]:
        if self._dimension == 0:
            raise Exception(
                "You are trying to use Biomes but have not picked a format. Use one of the convert methods to specify the format."
            )
        elif self._dimension == 2:
            self.convert_to_2d()
            return self._2d
        elif self._dimension == 3:
            self.convert_to_3d()
            return self._3d
        else:
            raise Exception("Dimension is invalid. This shouldn't happen")

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memodict=None):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result

    def __getattr__(self, item):
        return self._get_active().__getattribute__(item)

    def __getitem__(self, item):
        return self._get_active().__getitem__(item)

    def __setitem__(self, key, value):
        self._get_active().__setitem__(key, value)

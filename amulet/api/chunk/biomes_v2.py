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
"""

from typing import Tuple, Union, Dict, Optional
import numpy

Shape2D = Tuple[int, int]
Shape3D = Tuple[int, int, int]


def _validate_shape(shape: Tuple[int, ...], ndim: int):
    if not (len(shape) == ndim and all(1 <= s <= 16 for s in shape)):
        raise ValueError(f"Array must be {ndim}D array with power of 2 sizes.")


def _validate_data(data: Union[int, numpy.ndarray], ndim: int) -> numpy.ndarray:
    if isinstance(data, int):
        data = numpy.array(data).reshape((1,) * ndim)
    if not isinstance(data, numpy.ndarray):
        raise TypeError(f"{ndim}D data must be a numpy array.")
    _validate_shape(data.shape, ndim)
    return data


def _get_reshape_array(
    src_shape: Tuple[int, ...],
    dst_shape: Tuple[int, ...],
) -> Tuple[numpy.ndarray]:
    return tuple(
        numpy.meshgrid(
            *[s * numpy.arange(d) // d for s, d in zip(src_shape, dst_shape)],
            indexing="ij",
        )
    )


class Biomes:
    __slots__ = [
        "__biome_2d",
        "__biome_3d",
        "__default_biome",
    ]

    def __init__(
        self,
        raw_data: Union[
            None, numpy.ndarray, Dict[int, Union[int, numpy.ndarray]]
        ] = None,
        default_biome: int = 0,
    ):
        self.__biome_2d = None
        self.__biome_3d = {}
        self.__default_biome = default_biome

        if isinstance(raw_data, numpy.ndarray):
            _validate_data(raw_data, 2)
            self.__biome_2d = raw_data.astype(numpy.uint32)
        elif isinstance(raw_data, dict):
            for k, v in raw_data.items():
                if not isinstance(k, int):
                    raise TypeError("Keys must be ints.")
                self.__biome_3d[k] = _validate_data(v, 3)
        elif raw_data is not None:
            raise ValueError(f"Unsupported type {type(raw_data)}")

    @property
    def default_biome(self) -> int:
        return self.__default_biome

    @default_biome.setter
    def default_biome(self, default_biome: int):
        self.__default_biome = int(default_biome)

    def convert_2d_to_3d(self):
        """
        Convert from the 2D data to the 3D data.
        This will replace all the data in the 3D arrays with the data from the 2D array.
        If the 2D array is undefined this will do nothing.
        Note this method may cause some data loss through scaling artifacts and data replacement.
        """
        if self.__biome_2d is not None and self.__biome_3d:
            sx, sz = self.__biome_2d.shape
            arr = self.__biome_2d.reshape((sx, 1, sz))
            for cy in self.__biome_3d:
                self.__biome_3d[cy] = arr.copy()

    def convert_3d_to_2d(self, cy: Optional[int] = None):
        """
        Convert from the 3D data to the 2D data.
        This will replace the 2D array with data from the 3D array.
        If there is no array at cy then this will do nothing.
        Note this method may cause some data loss through scaling artifacts and data replacement.

        :param cy: The sub-chunk to use. If this is None (default) the highest sub-chunk will be used.
        """
        if cy is None and self.__biome_3d:
            cy = sorted(self.__biome_3d, key=lambda x: abs(x - 3))[0]
        if cy in self.__biome_3d:
            self.__biome_2d = self.__biome_3d[cy][:, -1, :].copy()

    @property
    def data_2d(self) -> Optional[numpy.ndarray]:
        """
        Get the raw 2D biome data for the chunk.
        This will not modify the data stored.
        Note this may be None if there is no data.

        :return: The raw data as it is stored.
        """
        return self.__biome_2d

    @data_2d.setter
    def data_2d(self, array: Optional[numpy.ndarray]):
        """
        Set the raw 2D biome data for the chunk.

        :param array: A numpy array to replace the data with. None to delete the data.
        """
        if array is not None:
            array = _validate_data(array, 2)
        self.__biome_2d = array

    @property
    def shape_2d(self) -> Optional[Shape2D]:
        """
        Get the shape of the 2D array.
        This will be None if the 2D data does not exist.
        """
        if self.__biome_2d is None:
            return None
        else:
            return self.__biome_2d.shape

    @shape_2d.setter
    def shape_2d(self, shape: Optional[Shape2D]):
        """
        Set the shape of the 2D array.
        If the array does not exist it will be populated from the 3D data or the default biome.
        If shape is None the array will be deleted.
        This will resize the stored array, potentially adding or destroying data that previously existed.

        :param shape: The shape to scale the array to. Must be a tuple of length 2 with values between 1 and 16.
        """
        if shape is None:
            self.__biome_2d = None
        else:
            self.__biome_2d = self.view_array_2d(shape)

    def view_array_2d(self, shape: Shape2D) -> numpy.ndarray:
        """
        View the 2D array for the chunk in the given shape.
        This does not modify the shape of the internal array.
        This should only be used for reading data because the returned array is not guaranteed to remain.

        :param shape: The shape to scale the array to. Must be a tuple of length 2 with values between 1 and 16.
        :return: The temporary reshaped array
        """
        _validate_shape(shape, 2)
        arr = self.__biome_2d
        if arr is None:
            # create the array
            if self.__biome_3d:
                arr = self.__biome_3d[
                    sorted(self.__biome_3d, key=lambda x: abs(x - 3))[0]
                ][:, -1, :].copy()
            else:
                return numpy.full(shape, self.__default_biome)
        if arr.shape != shape:
            # resize the array
            arr = arr[_get_reshape_array(arr.shape, shape)]
        return arr

    def get_array_2d(self, shape: Shape2D) -> numpy.ndarray:
        """
        Set the shape of the 2D array and return the result.
        This will resize the stored array, potentially adding or destroying data that previously existed.

        :param shape: The shape to get the array in. Must be a tuple of length 2 with values between 1 and 16.
        :return: The 2D biome array reshaped to the requested shape.
        """
        self.shape_2d = shape
        return self.__biome_2d

    @property
    def sub_chunks_3d(self) -> Tuple[int]:
        """Get a tuple of all sub-chunk indexes that are defined in the 3D data."""
        return tuple(self.__biome_3d)

    def has_array_3d(self, cy: int):
        """
        Check if an array is defined for a given sub-chunk.

        :param cy: The sub-chunk index to check.
        :return: True if the key is populated. False otherwise.
        """
        return cy in self.__biome_3d

    def get_data_3d(self, cy: int) -> numpy.ndarray:
        """
        Get the raw data for a given sub-chunk.
        This will not modify the data stored.

        :param cy: The sub-chunk index to get.
        :return: The raw array as it is stored.
        :raises KeyError if the requested item is not present.
        """
        return self.__biome_3d[cy]

    def get_shape_3d(self, cy: int) -> Shape3D:
        """
        Get the shape of the array for the given sub-chunk.

        :param cy: The sub-chunk index to get the shape of.
        :return: The shape of the array for the given sub-chunk.
        :raises KeyError if the requested item is not present.
        """
        return self.__biome_3d[cy].shape

    def set_shape_3d(self, cy: int, shape: Shape3D):
        """
        Set the shape of the 3D array for a given sub-chunk.
        If the array does not exist it will be populated from the 2D data, 3D data or the default biome.
        This will resize the stored array, potentially adding or destroying data that previously existed.

        :param cy: The sub-chunk index to resize.
        :param shape: The shape to scale the array to. Must be a tuple of length 3 with values between 1 and 16.
        """
        self.__biome_3d[cy] = self.view_array_3d(cy, shape)

    def view_array_3d(self, cy: int, shape: Shape3D) -> numpy.ndarray:
        """
        View the 3D array for the given sub-chunk in the given shape.
        This does not modify the shape of the internal array.
        This should only be used for reading data because the returned array is not guaranteed to remain.

        :param cy: The sub-chunk index to view.
        :param shape: The shape to scale the array to. Must be a tuple of length 3 with values between 1 and 16.
        :return:
        """
        _validate_shape(shape, 3)
        arr = self.__biome_3d.get(cy, None)
        if arr is None:
            # create the array
            if self.__biome_2d is not None:
                sx, sz = self.__biome_2d.shape
                arr = self.__biome_2d.copy().reshape((sx, 1, sz))
            elif self.__biome_3d:
                # find the nearest 3d array and populate from that
                arr = self.__biome_3d[
                    sorted(self.__biome_3d, key=lambda x: abs(x - cy))[0]
                ][:, -1:, :].copy()
            else:
                return numpy.full(shape, self.__default_biome)
        if arr.shape != shape:
            # resize the array
            arr = arr[_get_reshape_array(arr.shape, shape)]
        return arr

    def get_array_3d(self, cy: int, shape: Shape3D) -> numpy.ndarray:
        """
        Set the shape of the 3D array for a given sub-chunk and return the result.
        This will resize the stored array, potentially adding or destroying data that previously existed.

        :param cy: The sub-chunk index to get.
        :param shape: The shape to get the array in. Must be a tuple of length 3 with values between 1 and 16.
        :return: Numpy array resized to match shape
        """
        self.set_shape_3d(cy, shape)
        return self.get_data_3d(cy)

    def set_array_3d(self, cy: int, value: Union[int, numpy.ndarray]):
        """
        Set the array for a given sub-chunk.

        :param cy: The sub-chunk index to set.
        :param value: The array or value to set.
        """
        self.__biome_3d[cy] = _validate_data(value, 3)

    def delete_array_3d(self, cy: int):
        """
        Delete the array for the given sub-chunk.

        :param cy: The sub-chunk index to delete.
        """
        del self.__biome_3d[cy]

import numpy
from typing import Union, Optional, Dict
from copy import deepcopy


from amulet.api.partial_3d_array import UnboundedPartial3DArray


class Biomes3D(UnboundedPartial3DArray):
    def __init__(
        self, input_array: Optional[Union[Dict[int, numpy.ndarray], "Biomes3D"]] = None,
    ):
        if input_array is None:
            input_array = {}
        if isinstance(input_array, Biomes3D):
            input_array: dict = deepcopy(input_array._sections)
        if not isinstance(input_array, dict):
            raise Exception(f"Input array must be Biomes3D or dict, got {input_array}")
        super().__init__(numpy.uint32, 0, (4, 4, 4), (0, 16), sections=input_array)


class Biomes:
    def __init__(self, array: Union[numpy.ndarray, Biomes3D, Dict[int, numpy.ndarray]] = None):
        self._2d: Optional[numpy.ndarray] = None
        self._3d: Optional[Biomes3D] = None
        if array is None:
            self._mode = 3
        elif isinstance(array, numpy.ndarray):
            assert array.shape == (16, 16), "If Biomes is given an ndarray it must be 16x16"
            self._2d = array.copy()
            self._mode = 2
        elif isinstance(array, (dict, Biomes3D)):
            self._mode = 3
            self._3d = Biomes3D(array)

    def convert_to_2d(self):
        if self._2d is None:
            self._2d = numpy.zeros((16, 16), numpy.uint32)
        if self._mode == 3:
            # convert from 3D
            if self._3d is not None:
                self._2d[:, :] = numpy.kron(numpy.reshape(self._3d[:, 0, :], (4, 4)), numpy.ones((4, 4)))
            self._mode = 2

    def convert_to_3d(self):
        if self._3d is None:
            self._3d = Biomes3D()
        if self._mode == 2:
            # convert from 3D
            if self._2d is not None:
                self._3d[:, 0, :] = self._2d[::4, ::4]
            self._mode = 3

    def _get_active(self) -> Union[numpy.ndarray, Biomes3D]:
        if self._mode == 2:
            self.convert_to_2d()
            return self._2d
        elif self._mode == 3:
            self.convert_to_3d()
            return self._3d

    def __getattr__(self, item):
        return self._get_active().__getattribute__(item)

    def __getitem__(self, item):
        return self._get_active().__getitem__(item)

    def __setitem__(self, key, value):
        self._get_active().__setitem__(key, value)

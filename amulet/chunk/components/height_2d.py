from typing import Optional
import numpy


class Height2DComponent:
    __height: Optional[numpy.ndarray]

    def __init__(self) -> None:
        self.__height = None

    @property
    def height(self) -> numpy.ndarray:
        if self.__height is None:
            self.__height = numpy.zeros((16, 16), dtype=numpy.int64)
        return self.__height

    @height.setter
    def height(
        self,
        height: numpy.ndarray,
    ) -> None:
        height = numpy.asarray(height)
        if not isinstance(height, numpy.ndarray):
            raise TypeError
        if height.shape != (16, 16) or height.dtype != numpy.int64:
            raise ValueError
        self.__height = height

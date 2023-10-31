import numpy


class Height2DChunk:
    def __init__(self):
        self.__height = None

    @property
    def height(self) -> int:
        if self.__height is None:
            self.__height = numpy.zeros((16, 16), dtype=numpy.int64)
        return self.__height

    @height.setter
    def height(
        self,
        height: numpy.ndarray,
    ):
        height = numpy.asarray(height)
        if not isinstance(height, numpy.ndarray):
            raise TypeError
        if height.shape != (16, 16) or height.dtype != numpy.int64:
            raise ValueError
        self.__height = height

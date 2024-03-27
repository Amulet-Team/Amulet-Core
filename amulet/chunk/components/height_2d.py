import numpy
from numpy.typing import NDArray
from amulet.utils.typed_property import TypedProperty


# TODO: If numpy ever supports type hinting shape, add it here.
HeightType = NDArray[numpy.int64]


class Height2DComponent:
    __height: HeightType | None

    def __init__(self) -> None:
        self.__height = None

    @TypedProperty[HeightType, HeightType | object]
    def height(self) -> HeightType:
        if self.__height is None:
            self.__height = numpy.zeros((16, 16), dtype=numpy.int64)
        return self.__height

    @height.setter
    def _set_height(
        self,
        height: HeightType | object,
    ) -> None:
        height = numpy.asarray(height)
        if not isinstance(height, numpy.ndarray):
            raise TypeError
        if height.shape != (16, 16) or height.dtype != numpy.int64:
            raise ValueError
        self.__height = height

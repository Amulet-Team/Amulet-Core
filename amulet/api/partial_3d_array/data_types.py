from typing import Union, Tuple, Type
import numpy

IntSlicesType = Tuple[int, int, int]
UnpackedSliceType = Tuple[int, int, int]
UnpackedSlicesType = Tuple[UnpackedSliceType, UnpackedSliceType, UnpackedSliceType]
SliceSlicesType = Tuple[slice, slice, slice]
SingleFlexibleSliceType = Union[int, numpy.integer, slice]
FlexibleSlicesType = Tuple[
    SingleFlexibleSliceType, SingleFlexibleSliceType, SingleFlexibleSliceType
]
DtypeType = Union[Type[numpy.dtype], Type[bool]]

Integer = (int, numpy.integer)

from typing import Union, Tuple
import numpy

IntSlicesType = Tuple[int, int, int]
SliceSlicesType = Tuple[slice, slice, slice]
SingleFlexibleSliceType = Union[int, numpy.integer, slice]
FlexibleSlicesType = Tuple[
    SingleFlexibleSliceType,
    SingleFlexibleSliceType,
    SingleFlexibleSliceType
]

Integer = (int, numpy.integer)

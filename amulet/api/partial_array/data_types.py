from typing import Union, Tuple
import numpy

IntSlicesType = Tuple[int, int, int]
SliceSlicesType = Tuple[slice, slice, slice]
FlexibleSlicesType = Tuple[
    Union[int, numpy.integer, slice],
    Union[int, numpy.integer, slice],
    Union[int, numpy.integer, slice],
]

Integer = (int, numpy.integer)

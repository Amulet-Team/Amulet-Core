import numpy
import math
from typing import Optional, Tuple, Union

from .data_types import (
    FlexibleSlicesType,
    SliceSlicesType,
    Integer,
    SingleFlexibleSliceType,
)


def sanitise_slice(
    start: Optional[int], stop: Optional[int], step: Optional[int], arr_size: int
) -> Tuple[int, int, int]:
    """Convert slices into a sane format
    0 is always before the first number and arr_size is always after the last number."""
    if step is None:
        step = 1
    elif step == 0:
        raise Exception("step cannot be 0")

    if start is None:
        if step > 0:
            start = 0
        else:
            start = arr_size - 1
    elif start < 0:
        start = arr_size + start

    if stop is None:
        if step > 0:
            stop = arr_size
        else:
            stop = -1
    elif stop < 0:
        stop = arr_size + stop

    if step < 0:
        start += 1
        stop += 1

    if step > 0:
        start = max(0, start)
        stop = min(stop, arr_size)
    elif step < 0:
        start = min(arr_size, start)
        stop = max(stop, 0)
    step_count = max((stop - start) / step, 0)
    stop = start + math.ceil(step_count) * step

    return start, stop, step


def unsanitise_slice(
    start: int, stop: int, step: int, arr_size: int
) -> Tuple[int, int, int]:
    """Convert sanitised slices back to the normal format."""
    if step < 0:
        start -= 1
        stop -= 1
        if start < 0:
            start -= arr_size
        if stop < 0:
            stop -= arr_size

    return start, stop, step


def unpack_slice(item: slice):
    return item.start, item.stop, item.step


def to_slice(item: SingleFlexibleSliceType) -> slice:
    if isinstance(item, Integer):
        item = int(item)
        return slice(item, item + 1, 1)
    elif isinstance(item, slice):
        step = item.step
        if step == 0:
            raise Exception("Step of 0 is invalid")
        return slice(item.start, item.stop, 1 if step is None else step)
    else:
        raise Exception(f"Unsupported slice item {item}")


def multi_to_slice(slices: FlexibleSlicesType) -> SliceSlicesType:
    slices_out = []
    for item in slices:
        slices_out.append(to_slice(item))

    return tuple(slices_out)


def get_sliced_array_size(
    start: Optional[int], stop: Optional[int], step: Optional[int], arr_size
) -> int:
    """Find the size of the array the slice would produce from an array of size arr_size"""
    start, stop, step = sanitise_slice(start, stop, step, arr_size)
    return (stop - start) // step


def get_unbounded_slice_size(
    start: Optional[int], stop: Optional[int], step: Optional[int],
) -> Union[int, float]:
    if step is None:
        step = 1
    if start is None or stop is None:
        return math.inf
    return max(math.ceil((stop - start) / step), 0)

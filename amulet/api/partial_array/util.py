import numpy
import math
from typing import Optional, Tuple

from .data_types import FlexibleSlicesType, SliceSlicesType, Integer


def sanitise_slice(start, stop, step, arr_size) -> Tuple[int, int, int]:
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


def get_sliced_array_size(
        start: Optional[int],
        stop: Optional[int],
        step: Optional[int],
        arr_size
) -> int:
    """Find the size of the array the slice would produce from an array of size arr_size"""
    start_, stop_, step_ = sanitise_slice(start, stop, step, arr_size)
    return (stop_ - start_)//step_


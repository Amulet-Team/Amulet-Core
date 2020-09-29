import math
from typing import Optional, Tuple

from .data_types import (
    FlexibleSlicesType,
    SliceSlicesType,
    Integer,
    SingleFlexibleSliceType,
)


def _sanitise_slice(start: int, stop: int, step: int) -> Tuple[int, int, int]:
    step_count = math.ceil(max((stop - start) / step, 0))
    stop = start + step_count * step
    if step_count:
        stop += int(math.copysign(1, step)) - step

    return start, stop, step


def sanitise_slice(
    start: Optional[int], stop: Optional[int], step: Optional[int], arr_size: int
) -> Tuple[int, int, int]:
    """Convert slices into a sane format
    0 is always before the first number and arr_size is always after the last number."""
    # set default values
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

    # cap at the ends
    if step > 0:
        start = max(0, start)
        stop = min(stop, arr_size)
    elif step < 0:
        start = min(arr_size, start)
        stop = max(stop, 0)

    return _sanitise_slice(start, stop, step)


def sanitise_unbounded_slice(
    start: Optional[int],
    stop: Optional[int],
    step: Optional[int],
    default_min: int,  # the minimum value to default to
    default_max: int,  # the maximum value to default to
) -> Tuple[int, int, int]:
    if step is None:
        step = 1
    elif step == 0:
        raise Exception("step cannot be 0")

    # cap at the normal limits
    if step > 0:
        if start is None:
            start = default_min
        if stop is None:
            stop = default_max
    else:
        if start is None:
            start = default_max
        if stop is None:
            stop = default_min

    if step < 0:
        start += 1
        stop += 1

    return _sanitise_slice(start, stop, step)


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


def stack_sanitised_slices(
    start1: int, stop1: int, step1: int, start2: int, stop2: int, step2: int
) -> Tuple[int, int, int]:
    step3 = step1 * step2
    start3 = start1 + start2 * step1
    stop3 = start1 + stop2 * step1

    return _sanitise_slice(start3, stop3, step3)


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
    return tuple(to_slice(item) for item in slices)


def get_sliced_array_size(
    start: Optional[int], stop: Optional[int], step: Optional[int], arr_size
) -> int:
    """Find the size of the array the slice would produce from an array of size arr_size"""
    start, stop, step = sanitise_slice(start, stop, step, arr_size)
    return get_sanitised_sliced_array_size(start, stop, step)


def get_sanitised_sliced_array_size(start: int, stop: int, step: int):
    """Find the size of a slice that has been pre-sanitised"""
    return math.ceil((stop - start) / step)

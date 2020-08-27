from typing import overload, Tuple, Union, Optional, Type, Dict
import numpy

from .base_partial_3d_array import BasePartial3DArray
from .unbounded_partial_3d_array import UnboundedPartial3DArray
from .util import to_slice, sanitise_slice, unpack_slice


class BoundedPartial3DArray(BasePartial3DArray):
    """This class should behave the same as a numpy array in all three axis
    but the data internally is stored in chunks to minimise memory usage.
    The array has a fixed size in all three axis much like a numpy array."""

    @classmethod
    def from_partial_array(
        cls,
        parent_array: UnboundedPartial3DArray,
        start: Tuple[int, int, int],
        stop: Tuple[int, int, int],
        step: Tuple[int, int, int],
    ):
        return cls(
            parent_array.dtype,
            parent_array.default_value,
            parent_array.section_shape,
            start,
            stop,
            step,
            parent_array,
        )

    def __init__(
            self,
            dtype: Type[numpy.dtype],
            default_value: Union[int, bool],
            section_shape: Tuple[int, int, int],
            start: Tuple[Optional[int], int, Optional[int]],
            stop: Tuple[Optional[int], int, Optional[int]],
            step: Tuple[Optional[int], Optional[int], Optional[int]],
            parent_array: UnboundedPartial3DArray,
    ):
        assert isinstance(start[1], int) and isinstance(stop[1], int), "start[1] and stop[1] must both be ints."
        assert isinstance(parent_array, UnboundedPartial3DArray)
        super().__init__(
            dtype,
            default_value,
            section_shape,
            start,
            stop,
            step,
            parent_array
        )

    @overload
    def __getitem__(self, slices: Tuple[int, int, int]) -> int:
        ...

    @overload
    def __getitem__(
        self, slices: Tuple[Union[int, slice], Union[int, slice], Union[int, slice]]
    ) -> "BoundedPartial3DArray":
        ...

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if len(item) != 3:
                raise Exception(f"Tuple item must be of length 3, got {len(item)}")
            if all(isinstance(i, (int, numpy.integer)) for i in item):
                abs_item = [0, 0, 0]
                starts = (self.start_x, self.start_y, self.start_z)
                stops = (self.stop_x, self.stop_y, self.stop_z)
                steps = (self.step_x, self.step_y, self.step_z)
                for axis in range(3):
                    value = item[axis]
                    start = starts[axis]
                    stop = stops[axis]
                    step = steps[axis]
                    if value >= 0:
                        value = start + value * step
                    else:
                        value = stop + value * step

                    if step > 0:
                        if not start <= value < stop:
                            raise IndexError(f"index {item[1]} is out of bounds for axis {axis} with size {self.shape[axis]}")
                    else:
                        if not start >= value > stop:
                            raise IndexError(f"index {item[1]} is out of bounds for axis {axis} with size {self.shape[axis]}")
                        value -= 1

                    abs_item[axis] = value

                x, y, z = abs_item

                cy = y // self.section_shape[1]
                if cy in self:
                    return int(
                        self._sections[cy][
                            (x, y % self.section_shape[1], z)
                        ]
                    )
                else:
                    return self.default_value

            elif all(isinstance(i, (int, numpy.integer, slice)) for i in item):
                raise NotImplementedError
            else:
                raise Exception(f"Unsupported tuple {item} for getitem")

        elif isinstance(item, numpy.ndarray):
            raise NotImplementedError(
                "numpy.ndarray is not currently supported as a slice input"
            )
        else:
            raise Exception(
                f"{item.__class__.__name__}({item}) is not a supported input for __getitem__"
            )

    def __setitem__(self, key, value):
        raise NotImplementedError

from typing import overload, Tuple, Union, Optional, Type, Generator
import numpy
import math

from .data_types import SliceSlicesType, UnpackedSlicesType
from .base_partial_3d_array import BasePartial3DArray
from .unbounded_partial_3d_array import UnboundedPartial3DArray
from .util import to_slice, sanitise_slice, unpack_slice, stack_sanitised_slices


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

    def __array__(self):
        """Convert the data to a numpy array"""
        array = numpy.full(self.shape, self.default_value, self.dtype)
        for sy, slices, relative_slices in self._iter_slices((
                (self.start_x, self.stop_x, self.step_x),
                (self.start_y, self.stop_y, self.step_y),
                (self.start_z, self.stop_z, self.step_z),
        )):
            if sy in self._sections:
                array[relative_slices] = self._sections[sy][slices]
        return array

    def _iter_slices(self, slices: UnpackedSlicesType) -> Generator[Tuple[int, SliceSlicesType, SliceSlicesType], None, None]:
        """
        split the sanitised slice into section based slices
        :return: Generator of section y, section slice, relative slice
        """
        slice_x = slice(*slices[0])
        slice_z = slice(*slices[2])
        relative_slice_x = slice(None)
        relative_slice_z = slice(None)

        start_y, stop_y, step_y = slices[1]
        sy = None
        section_start_y = None
        section_stop_y = None
        section_start_dy = None
        section_stop_dy = None
        for y in range(start_y, stop_y, step_y):
            sy_, dy_ = self._section_index(y)
            if sy_ != sy:
                # we are in a new section
                if sy is not None:
                    yield sy, \
                          (
                              slice_x,
                              slice(section_start_dy, section_stop_dy, step_y),
                              slice_z
                          ), \
                          (
                              relative_slice_x,
                              slice(
                                  math.ceil((section_start_y - start_y) / step_y),
                                  math.ceil((section_stop_y - start_y) / step_y)
                              ),
                              relative_slice_z
                          )
                sy = sy_
                section_start_y = y
                section_start_dy = dy_
            section_stop_y = y + int(math.copysign(1, step_y))
            section_stop_dy = dy_ + int(math.copysign(1, step_y))
        if sy is not None:
            yield sy, \
                  (
                      slice_x,
                      slice(section_start_dy, section_stop_dy, step_y),
                      slice_z
                  ), \
                  (
                      relative_slice_x,
                      slice(
                          math.ceil((section_start_y - start_y) / step_y),
                          math.ceil((section_stop_y - start_y) / step_y)
                      ),
                      relative_slice_z
                  )

    def _relative_to_absolute(self, axis: int, relative_index: int) -> int:
        """Convert a relative index to the absolute value in the array."""
        value = relative_index
        start = self.start[axis]
        stop = self.stop[axis]
        step = self.step[axis]
        if value >= 0:
            value = start + value * step
        else:
            stop_max = start + math.ceil((stop - start) / step) * step
            value = stop_max + value * step

        if step > 0:
            if not start <= value < stop:
                raise IndexError(f"index {relative_index} is out of bounds for axis {axis} with size {self.shape[axis]}")
        else:
            if not start >= value > stop:
                raise IndexError(f"index {relative_index} is out of bounds for axis {axis} with size {self.shape[axis]}")
            value -= 1

        return value

    def _section_index(self, y: int) -> Tuple[int, int]:
        """Get the section index and location within the section of an absolute y coordinate"""
        return y // self.section_shape[1], y % self.section_shape[1]

    def _stack_slices(self, slices: Tuple[slice, slice, slice]) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
        return tuple(
            stack_sanitised_slices(
                start,
                stop,
                step,
                *sanitise_slice(
                    *unpack_slice(
                        to_slice(i)
                    ),
                    shape
                )
            )
            for i, start, stop, step, shape in zip(slices, self.start, self.stop, self.step, self.shape)
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
                raise KeyError(f"Tuple item must be of length 3, got {len(item)}")
            if all(isinstance(i, (int, numpy.integer)) for i in item):
                x, y, z = tuple(self._relative_to_absolute(axis, item[axis]) for axis in range(3))

                sy, dy = self._section_index(y)
                if sy in self:
                    return int(
                        self._sections[sy][
                            (x, dy, z)
                        ]
                    )
                else:
                    return self.default_value

            elif all(isinstance(i, (int, numpy.integer, slice)) for i in item):
                item: Tuple[
                    Tuple[int, int, int],
                    Tuple[int, int, int],
                    Tuple[int, int, int],
                ] = zip(
                    *self._stack_slices(item)
                )

                return BoundedPartial3DArray.from_partial_array(
                    self._parent_array,
                    *item
                )
            else:
                raise KeyError(f"Unsupported tuple {item} for getitem")

        elif isinstance(item, (numpy.ndarray, BoundedPartial3DArray)):
            raise NotImplementedError(
                "numpy.ndarray is not currently supported as a slice input"
            )
        else:
            raise KeyError(
                f"{item.__class__.__name__}({item}) is not a supported input for __getitem__"
            )

    def __setitem__(self, item, value):
        if isinstance(item, tuple):
            if len(item) != 3:
                raise KeyError(f"Tuple item must be of length 3, got {len(item)}")
            elif all(isinstance(i, (int, numpy.integer, slice)) for i in item):
                stacked_slices: Tuple[
                    Tuple[int, int, int],
                    Tuple[int, int, int],
                    Tuple[int, int, int],
                ] = self._stack_slices(item)
                if (isinstance(value, (int, numpy.integer)) and numpy.issubdtype(self.dtype, numpy.integer)) or (isinstance(value, bool) and numpy.issubdtype(self.dtype, numpy.bool)):
                    for sy, slices, _ in self._iter_slices(stacked_slices):
                        if sy in self._sections:
                            self._sections[sy][slices] = value
                        elif value != self.default_value:
                            self._parent_array.create_section(sy)
                            self._sections[sy][slices] = value
                elif isinstance(value, (numpy.ndarray, BoundedPartial3DArray)) and (numpy.issubdtype(value.dtype, numpy.integer) and numpy.issubdtype(self.dtype, numpy.integer)) or (numpy.issubdtype(value.dtype, numpy.bool) and numpy.issubdtype(self.dtype, numpy.bool)):
                    size_array = self[item]
                    if size_array.shape != value.shape:
                        raise ValueError(f"The shape of the index ({size_array.shape}) and the shape of the given array ({value.shape}) do not match.")
                    for sy, slices, relative_slices in size_array._iter_slices(stacked_slices):
                        if sy not in self._sections:
                            self._parent_array.create_section(sy)
                        self._sections[sy][slices] = numpy.asarray(value[relative_slices])
                else:
                    raise ValueError(f"Bad value {value}")

            else:
                raise KeyError(f"Unsupported tuple {item} for getitem")
        elif isinstance(item, (numpy.ndarray, BoundedPartial3DArray)):
            raise NotImplementedError(
                "numpy.ndarray is not currently supported as a slice input"
            )
        else:
            raise KeyError(
                f"{item.__class__.__name__}({item}) is not a supported input for __getitem__"
            )

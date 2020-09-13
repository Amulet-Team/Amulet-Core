from typing import Optional, Dict, Union, Tuple, Type, TYPE_CHECKING
import numpy

import copy

from .util import get_sanitised_sliced_array_size
from .data_types import DtypeType, UnpackedSlicesType

if TYPE_CHECKING:
    from .unbounded_partial_3d_array import UnboundedPartial3DArray


class BasePartial3DArray:
    """Do not use this class directly. Use UnboundedPartial3DArray or BoundedPartial3DArray"""

    def __init__(
        self,
        dtype: DtypeType,
        default_value: Union[int, bool],
        section_shape: Tuple[int, int, int],
        start: Tuple[Optional[int], Optional[int], Optional[int]],
        stop: Tuple[Optional[int], Optional[int], Optional[int]],
        step: Tuple[Optional[int], Optional[int], Optional[int]],
        parent_array: Optional["UnboundedPartial3DArray"] = None,
        sections: Optional[Dict[int, numpy.ndarray]] = None,
    ):
        self._dtype = dtype
        self._default_value: Union[int, bool] = default_value
        self._section_shape = section_shape
        self._parent_array = parent_array

        self._size_x = None
        self._size_y = None
        self._size_z = None

        self._start_x, self._stop_x, self._step_x = start[0], stop[0], step[0]
        self._start_y, self._stop_y = start[1], stop[1]
        assert (self._start_y is None and self._stop_y is None) or (
            isinstance(self._start_y, int) and isinstance(self._stop_y, int)
        ), "y start and stop must both be None or ints"
        self._step_y = 1 if step[1] is None else step[1]
        if self.size_y == 0:
            self._stop_y = self._start_y
        self._start_z, self._stop_z, self._step_z = start[2], stop[2], step[2]

        if parent_array is None:
            # populate from sections
            self._sections: Dict[int, numpy.ndarray] = sections or {}
            for key, section in self._sections.items():
                assert isinstance(key, int), "All keys must be ints"
                assert (
                    section.shape == self._section_shape
                ), "The size of all sections must be equal to the section_shape."
                assert (
                    section.dtype == self._dtype
                ), "The given dtype does not match the arrays given."

        elif isinstance(parent_array, BasePartial3DArray):
            # populate from the array
            assert (
                parent_array.section_shape == self._section_shape
            ), "The parent section shape must match the given section_shape."
            assert (
                parent_array.dtype == self._dtype
            ), "The parent dtype must match the given dtype"
            self._sections = parent_array._sections

        else:
            raise Exception(
                f"{parent_array.__class__.__name__}({parent_array}) is not a valid input type for parent_array"
            )

    @property
    def start_x(self) -> int:
        return self._start_x

    @property
    def start_y(self) -> int:
        return self._start_y

    @property
    def start_z(self) -> int:
        return self._start_z

    @property
    def start(self) -> Tuple[int, int, int]:
        return self.start_x, self.start_y, self.start_z

    @property
    def stop_x(self) -> int:
        return self._stop_x

    @property
    def stop_y(self) -> int:
        return self._stop_y

    @property
    def stop_z(self) -> int:
        return self._stop_z

    @property
    def stop(self) -> Tuple[int, int, int]:
        return self.stop_x, self.stop_y, self.stop_z

    @property
    def step_x(self) -> int:
        return self._step_x

    @property
    def step_y(self) -> int:
        return self._step_y

    @property
    def step_z(self) -> int:
        return self._step_z

    @property
    def step(self) -> Tuple[int, int, int]:
        return self.step_x, self.step_y, self.step_z

    @property
    def slice_x(self) -> slice:
        return slice(self.start_x, self.stop_x, self.step_x)

    @property
    def slice_y(self) -> slice:
        return slice(self.start_y, self.stop_y, self.step_y)

    @property
    def slice_z(self) -> slice:
        return slice(self.start_z, self.stop_z, self.step_z)

    @property
    def slices_tuple(self) -> UnpackedSlicesType:
        return (
            (self.start_x, self.stop_x, self.step_x),
            (self.start_y, self.stop_y, self.step_y),
            (self.start_z, self.stop_z, self.step_z),
        )

    @property
    def size_x(self) -> int:
        if self._size_x is None:
            self._size_x = get_sanitised_sliced_array_size(
                self.start_x, self.stop_x, self.step_x
            )
        return self._size_x

    @property
    def size_y(self) -> Union[int, float]:
        if self._size_y is None:
            self._size_y = get_sanitised_sliced_array_size(
                self.start_y, self.stop_y, self.step_y
            )
        return self._size_y

    @property
    def size_z(self) -> int:
        if self._size_z is None:
            self._size_z = get_sanitised_sliced_array_size(
                self.start_z, self.stop_z, self.step_z
            )
        return self._size_z

    @property
    def shape(self) -> Tuple[int, Union[int, float], int]:
        return self.size_x, self.size_y, self.size_z

    @property
    def dtype(self) -> Type[numpy.dtype]:
        return self._dtype

    @property
    def default_value(self) -> Union[int, bool]:
        """The default value to populate undefined sections with."""
        return self._default_value

    @property
    def section_shape(self) -> Tuple[int, int, int]:
        return self._section_shape

    def _section_index(self, y: int) -> Tuple[int, int]:
        """Get the section index and location within the section of an absolute y coordinate"""
        return y // self.section_shape[1], y % self.section_shape[1]

    def __array__(self, dtype=None):
        raise NotImplementedError

    def __contains__(self, item: int):
        return item in self._sections

    def __iter__(self):
        raise Exception(
            "Please use sections method if this is what you are trying to achieve"
        )

    def __getitem__(self, item):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def copy(self):
        return copy.copy(self)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memodict=None):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memodict))
        return result

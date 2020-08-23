from typing import Optional, Dict, Union, Tuple, Generator, overload, Iterable, Type
import numpy
import math

from .util import (
    get_sliced_array_size,
    sanitise_slice,
    get_unbounded_slice_size
)


class Partial3DArray:
    """This is designed to work similarly to a numpy.ndarray but stores the data in a very different way.
    A numpy.ndarray stores a fixed size continuous array which for large arrays can become unmanageable.
    Sparse arrays allow individual values to exist which can be great where a small set of values are
    defined in a large area but can be less efficient in some cases than a continuous array.

    This class was born out of the need for an array that has a fixed size in the horizontal distances but an
    unlimited height in the vertical distance (both above and below the origin)
    This is achieved by splitting the array into sections of fixed height and storing them sparsely so that only
    the defined sections need to be held in memory.

    This class also implements an API that resembles that of the numpy.ndarray but it is not directly compatible with numpy.
    Chained indexing does not currently work as __getitem__ returns a copy of the array data rather than a view into it.
    To use numpy fully the section data will need to be directly used.
    """

    @classmethod
    def from_partial_array(
            cls,
            parent_array: "Partial3DArray",
            start: Tuple[int, Optional[int], int],
            stop: Tuple[int, Optional[int], int],
            step: Tuple[int, int, int]
    ):
        return cls(
            parent_array.dtype,
            parent_array.default_value,
            parent_array.section_shape,
            start,
            stop,
            step,
            parent_array=parent_array
        )

    @classmethod
    def from_sections(
            cls,
            dtype: Type[numpy.dtype],
            default_value: Union[int, bool],
            section_shape: Tuple[int, int, int],
            sections: Dict[int, numpy.ndarray],
            start: Tuple[int, Optional[int], int],
            stop: Tuple[int, Optional[int], int],
            step: Tuple[int, int, int],
    ):
        return cls(
            dtype,
            default_value,
            section_shape,
            start,
            stop,
            step,
            sections=sections,
        )

    def __init__(
            self,
            dtype: Type[numpy.dtype],
            default_value: Union[int, bool],
            section_shape: Tuple[int, int, int],
            start: Tuple[Optional[int], Optional[int], Optional[int]],
            stop: Tuple[Optional[int], Optional[int], Optional[int]],
            step: Tuple[Optional[int], Optional[int], Optional[int]],
            parent_array: Optional["Partial3DArray"] = None,
            sections: Optional[Dict[int, numpy.ndarray]] = None
    ):
        self._dtype = dtype
        self._default_value: Union[int, bool] = default_value
        self._section_shape = section_shape
        self._parent_array = parent_array

        self._size_x = None
        self._size_y = None
        self._size_z = None

        self._start_x, self._stop_x, self._step_x = sanitise_slice(start[0], stop[0], step[0], self._section_shape[0])
        self._start_y, self._stop_y = start[1], stop[1]
        assert (self._start_y is None and self._stop_y is None) or (isinstance(self._start_y, int) and isinstance(self._stop_y, int)), "y start and stop must both be None or ints"
        self._step_y = 1 if step[1] is None else step[1]
        if self.size_y == 0:
            self._stop_y = self._start_y
        self._start_z, self._stop_z, self._step_z = sanitise_slice(start[2], stop[2], step[2], self._section_shape[2])

        if parent_array is None:
            # populate from sections
            self._sections: Dict[int, numpy.ndarray] = sections or {}
            for key, section in self._sections.items():
                assert isinstance(key, int), "All keys must be ints"
                assert section.shape == self._section_shape, "The size of all sections must be equal to the section_shape."
                assert section.dtype == self._dtype, "The given dtype does not match the arrays given."

        elif isinstance(parent_array, Partial3DArray):
            # populate from the array
            assert parent_array.section_shape == self._section_shape, "The parent section shape must match the given section_shape."
            assert parent_array.dtype == self._dtype, "The parent dtype must match the given dtype"
            self._sections = parent_array._sections

        else:
            raise Exception(f"{parent_array.__class__.__name__}({parent_array}) is not a valid input type for parent_array")

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
    def stop_x(self) -> int:
        return self._stop_x

    @property
    def stop_y(self) -> int:
        return self._stop_y

    @property
    def stop_z(self) -> int:
        return self._stop_z

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
    def size_x(self) -> int:
        if self._size_x is None:
            self._size_x = get_sliced_array_size(self.start_x, self.stop_x, self.step_x, self._section_shape[0])
        return self._size_x

    @property
    def size_y(self) -> Union[int, float]:
        if self._size_y is None:
            self._size_y = get_unbounded_slice_size(self.start_y, self.stop_y, self.step_y)
        return self._size_y

    @property
    def size_z(self) -> int:
        if self._size_z is None:
            self._size_z = get_sliced_array_size(self.start_z, self.stop_z, self.step_z, self._section_shape[2])
        return self._size_z

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

    # def __array__(self):
    #     raise NotImplementedError  # todo

    def __contains__(self, item: int):
        return item in self._sections

    def __iter__(self):
        raise NotImplementedError(
            "Please use sections method if this is what you are trying to achieve"
        )

    @property
    def sections(self) -> Iterable[int]:
        """An iterable of the section indexes that exist"""
        return self._sections.keys()

    def create_section(self, cy: int):
        if self._parent_array is None:
            self._sections[cy] = numpy.full(
                self.section_shape,
                self.default_value,
                dtype=self._dtype
            )
        else:
            self._parent_array.create_section(cy)

    def add_section(self, cy: int, section: numpy.ndarray):
        if self._parent_array is None:
            assert section.shape == self._section_shape, "The size of all sections must be equal to the section_shape."
            assert section.dtype == self._dtype, "the given dtype does not match the arrays given."
        else:
            self._parent_array.add_section(cy, section)

    def get_section(self, cy: int) -> numpy.ndarray:
        """Get the section ndarray for a given section index.
        :param cy: The section y index
        :return: Numpy array for this section
        :raises: KeyError if no section exists with this index
        """
        if cy not in self._sections:
            self.create_section(cy)
        return self._sections[cy]

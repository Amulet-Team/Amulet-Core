from typing import Union, Tuple, overload, Iterable, Optional, Dict
import numpy
import math

from .base_partial_3d_array import BasePartial3DArray
from .util import sanitise_slice, to_slice, unpack_slice, sanitise_unbounded_slice
from .data_types import DtypeType


class UnboundedPartial3DArray(BasePartial3DArray):
    """This is designed to work similarly to a numpy.ndarray but stores the data in a very different way.
    A numpy.ndarray stores a fixed size continuous array which for large arrays can become unmanageable.
    Sparse arrays allow individual values to exist which can be great where a small set of values are
    defined in a large area but can be less efficient in some cases than a continuous array.

    This class was born out of the need for an array that has a fixed size in the horizontal distances but an
    unlimited height in the vertical distance (both above and below the origin)
    This is achieved by splitting the array into sections of fixed height and storing them sparsely so that only
    the defined sections need to be held in memory.

    This class also implements an API that resembles that of the numpy.ndarray but it is not directly compatible with numpy.
    This class implements methods to access and directly modify the underlying numpy arrays to give finer control.
    """

    def __init__(
        self,
        dtype: DtypeType,
        default_value: Union[int, bool],
        section_shape: Tuple[int, int, int],
        default_section_counts: Tuple[int, int],
        sections: Optional[Dict[int, numpy.ndarray]] = None,
    ):
        super().__init__(
            dtype,
            default_value,
            section_shape,
            (0, None, 0),
            (section_shape[0], None, section_shape[0]),
            (1, 1, 1),
            sections=sections,
        )
        self._default_min_y = -default_section_counts[0] * self.section_shape[1]
        self._default_max_y = default_section_counts[1] * self.section_shape[1]

    def __repr__(self):
        return f"UnboundedPartial3DArray(dtype={self.dtype}, shape={self.shape})"

    @property
    def size_y(self) -> float:
        return math.inf

    @property
    def sections(self) -> Iterable[int]:
        """An iterable of the section indexes that exist"""
        return self._sections.keys()

    def create_section(self, sy: int):
        self._sections[sy] = numpy.full(
            self.section_shape, self.default_value, dtype=self._dtype
        )

    def add_section(self, sy: int, section: numpy.ndarray):
        assert (
            section.shape == self._section_shape
        ), "The size of all sections must be equal to the section_shape."
        if section.dtype != self._dtype:
            section = section.astype(self._dtype)
        self._sections[sy] = section

    def get_section(self, sy: int) -> numpy.ndarray:
        """Get the section ndarray for a given section index.
        :param sy: The section y index
        :return: Numpy array for this section
        :raises: KeyError if no section exists with this index
        """
        if sy not in self._sections:
            self.create_section(sy)
        return self._sections[sy]

    def __setitem__(
        self,
        slices: Tuple[Union[int, slice], Union[int, slice], Union[int, slice]],
        value: Union[int, numpy.integer, numpy.ndarray],
    ):
        if isinstance(value, (int, numpy.integer)) and all(
            isinstance(s, (int, numpy.integer)) for s in slices
        ):
            sy, dy = self._section_index(slices[1])
            self.get_section(sy)[(slices[0], dy, slices[2])] = value
        else:
            self[slices][:, :, :] = value

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
                sy = item[1] // self.section_shape[1]
                if sy in self:
                    return int(
                        self._sections[sy][
                            (item[0], item[1] % self.section_shape[1], item[2])
                        ]
                    )
                else:
                    return self.default_value

            elif all(isinstance(i, (int, numpy.integer, slice)) for i in item):
                start_x, stop_x, step_x = sanitise_slice(
                    *unpack_slice(to_slice(item[0])), self.size_x
                )
                start_y, stop_y, step_y = sanitise_unbounded_slice(
                    *unpack_slice(to_slice(item[1])),
                    self._default_min_y,
                    self._default_max_y,
                )
                start_z, stop_z, step_z = sanitise_slice(
                    *unpack_slice(to_slice(item[2])), self.size_z
                )

                return BoundedPartial3DArray.from_partial_array(
                    self,
                    (start_x, start_y, start_z),
                    (stop_x, stop_y, stop_z),
                    (step_x, step_y, step_z),
                )
            else:
                raise KeyError(f"Unsupported tuple {item} for getitem")

        else:
            raise KeyError(
                f"{item.__class__.__name__}({item}) is not a supported input for __getitem__"
            )


from .bounded_partial_3d_array import BoundedPartial3DArray

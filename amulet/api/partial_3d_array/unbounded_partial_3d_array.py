from typing import Union, Tuple, overload, Iterable, Optional, Dict  # , Literal
import numpy
import math

from .base_partial_3d_array import BasePartial3DArray
from .util import sanitise_slice, to_slice, unpack_slice, sanitise_unbounded_slice
from .data_types import DtypeType, Integer, IntegerType


class UnboundedPartial3DArray(BasePartial3DArray):
    """
    This is designed to work similarly to a numpy.ndarray but stores the data in a very different way.
    A numpy.ndarray stores a fixed size continuous array which for large arrays can become unmanageable.
    Sparse arrays allow individual values to exist which can be great where a small set of values are
    defined in a large area but get less efficient the denser the defined values are.

    This class was born out of the need for an array that has a fixed size in the horizontal directions but an
    unlimited height in the vertical distance (both above and below the origin)
    This is achieved by splitting the array into sections of fixed height and storing them sparsely so that only
    the defined sections need to be held in memory.

    This class implements an API that resembles that of a numpy array but it is not directly compatible with numpy.
    This class also implements methods to access and directly modify the underlying numpy arrays to give finer control.
    """

    def __init__(
        self,
        dtype: DtypeType,
        default_value: Union[int, bool],
        section_shape: Tuple[int, int, int],
        default_section_counts: Tuple[int, int],
        sections: Optional[Dict[int, numpy.ndarray]] = None,
    ):
        """
        Construct a :class:`UnboundedPartial3DArray`. This should not be used directly. You should use the relevant subclass for your use.

        :param dtype: The dtype that all arrays will be stored in.
        :param default_value: The default value that all undefined arrays will be populated with if required.
        :param section_shape: The shape of each section array.
        :param default_section_counts: A tuple containing the default number of sections above and below the origin in the y axis. This is used to define the default bounds.
        :param sections: The sections to initialise the array with.
        """
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
    def size_y(self) -> float:  # Literal[math.inf]:
        """The size of the array in the y axis. Is always :attr:`math.inf` for the unbounded variant. Read Only"""
        return math.inf

    @property
    def sections(self) -> Iterable[int]:
        """An iterable of the section defined in the array."""
        return self._sections.keys()

    def create_section(self, sy: IntegerType):
        """
        Create a section array at the given location using the default value and dtype.

        :param sy: The section index to create.
        """
        self._sections[int(sy)] = numpy.full(
            self.section_shape, self.default_value, dtype=self._dtype
        )

    def has_section(self, sy: int) -> bool:
        """Check if the array for a given section exists.
        :param cy: The section y index
        :return: True if the array exists, False otherwise
        """
        return sy in self._sections

    def add_section(self, sy: IntegerType, section: numpy.ndarray):
        """
        Add a section array at the given location.

        :param sy: The section index to assign the array to.
        :param section: The array to assign to the section. The shape must equal :attr:`section_shape`.
        """
        if section.shape != self._section_shape:
            raise ValueError(
                f"The size of all sections must be equal to the section_shape. Expected shape {self._section_shape}, got {section.shape}"
            )
        if section.dtype != self._dtype:
            section = section.astype(self._dtype)
        self._sections[int(sy)] = section

    def get_section(self, sy: Union[int, numpy.integer]) -> numpy.ndarray:
        """
        Get the section array for a given section index.

        If the section is not defined it will be populated using :meth:`create_section`

        :param sy: The section index to get.
        :return: Numpy array for this section
        """
        if sy not in self._sections:
            self.create_section(int(sy))
        return self._sections[sy]

    def __setitem__(
        self,
        slices: Tuple[
            Union[IntegerType, slice],
            Union[IntegerType, slice],
            Union[IntegerType, slice],
        ],
        value: Union[int, numpy.integer, numpy.ndarray],
    ):
        """
        Set a sub-section of the infinite height array.

        >>> # set the value at a given location
        >>> partial_array[3, 4, 5] = 1
        >>> # set a cuboid volume in the array
        >>> partial_array[2:3, 4:5, 6:7] = 1
        >>> # slice and int can be mixed
        >>> partial_array[2:3, 4, 6:7] = 1
        >>> # if an unbounded slice is given in the y axis it will be capped at the default max and min y values.
        >>> partial_array[2:3, :, 6:7] = 1

        :param slices: The slices or locations that define the volume to set.
        :param value: The value to set at the given location. Can be an integer or array.
        """
        if isinstance(value, Integer) and all(isinstance(s, Integer) for s in slices):
            sy, dy = self._section_index(slices[1])
            self.get_section(sy)[(slices[0], dy, slices[2])] = value
        else:
            self[slices][:, :, :] = value

    @overload
    def __getitem__(self, slices: Tuple[IntegerType, IntegerType, IntegerType]) -> int:
        ...

    @overload
    def __getitem__(
        self,
        slices: Tuple[
            Union[IntegerType, slice],
            Union[IntegerType, slice],
            Union[IntegerType, slice],
        ],
    ) -> "BoundedPartial3DArray":
        ...

    def __getitem__(self, item):
        """
        Get a value or sub-section of the unbounded array.

        >>> # get the value at a given location
        >>> value = partial_array[3, 4, 5]  # an integer
        >>> # get a cuboid volume in the array
        >>> value = partial_array[2:3, 4:5, 6:7]  # BoundedPartial3DArray
        >>> # slice and int can be mixed
        >>> value = partial_array[2:3, 4, 6:7]  # BoundedPartial3DArray
        >>> # if an unbounded slice is given in the y axis it will be capped at the default max and min y values.
        >>> value = partial_array[2:3, :, 6:7]  # BoundedPartial3DArray

        :param item: The slices to extract.
        :return: The value or BoundedPartial3DArray viewing into this array.
        """
        if isinstance(item, tuple):
            if len(item) != 3:
                raise KeyError(f"Tuple item must be of length 3, got {len(item)}")
            if all(isinstance(i, Integer) for i in item):
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

    def __array__(self, dtype=None):
        """
        Get the data contained within as a numpy array.

        The y axis will be clamped to the default minimum and maximum y values.

        >>> numpy.array(partial_array)

        :param dtype: The dtype of the returned numpy array.
        :return: A numpy array of the contained data.
        """
        return self[:, :, :].__array__(dtype)


from .bounded_partial_3d_array import BoundedPartial3DArray

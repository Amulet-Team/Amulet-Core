from typing import Union, Tuple, overload, Iterable, Type, Optional, Dict
import numpy

from .base_partial_3d_array import BasePartial3DArray
from .bounded_partial_3d_array import BoundedPartial3DArray


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
    Chained indexing does not currently work as __getitem__ returns a copy of the array data rather than a view into it.
    To use numpy fully the section data will need to be directly used.
    """

    def __init__(
            self,
            dtype: Type[numpy.dtype],
            default_value: Union[int, bool],
            section_shape: Tuple[int, int, int],
            default_section_counts: Tuple[int, int],
            sections: Optional[Dict[int, numpy.ndarray]] = None
    ):
        super().__init__(
            dtype,
            default_value,
            section_shape,
            (None, None, None),
            (None, None, None),
            (None, None, None),
            sections=sections
        )
        self._default_min_y = - default_section_counts[0] * self.section_shape[1]
        self._default_max_y = - default_section_counts[1] * self.section_shape[1]

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


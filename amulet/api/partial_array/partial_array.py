from typing import Optional, Dict, Union, Tuple, Generator, overload, Iterable
import numpy
import math

flat_16 = numpy.zeros((16, 16), dtype=bool)


class PartialNDArray:
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
    _size_x = 0
    _section_size_y = 0
    _size_z = 0

    def __init__(
        self,
        input_array: Optional[Union[Dict[int, numpy.ndarray], "PartialNDArray"]] = None,
    ):
        if self._check_type(input_array):
            input_array = {
                cy: input_array.get_section(cy).copy()
                for cy in input_array.sections
            }
        elif not isinstance(input_array, dict):
            input_array = {}
        self._sections: Dict[int, numpy.ndarray] = input_array

    def _check_type(self, other) -> bool:
        return isinstance(other, PartialNDArray)

    @property
    def size_x(self) -> int:
        """The size of the array in the first dimension"""
        return self._size_x

    @property
    def section_size_y(self) -> int:
        """The size of a single section in the array in the second dimension"""
        return self._section_size_y

    @property
    def size_z(self) -> int:
        """The size of the array in the third dimension"""
        return self._size_z

    def _section_y(self, y: int) -> int:
        """The section index a given y index corresponds to."""
        return int(y // self.section_size_y)

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

    def get_create_section(self, cy: int) -> numpy.ndarray:
        """Get the section ndarray for a given section index. Create if it does not exist.
        :param cy: The section y index
        :return: Numpy array for this section
        """
        if cy not in self._sections:
            self._sections[cy] = numpy.zeros((16, 16, 16), dtype=numpy.uint64)
        return self._sections[cy]

    def get_section(self, cy: int) -> numpy.ndarray:
        """Get the section ndarray for a given section index.
        :param cy: The section y index
        :return: Numpy array for this section
        :raises: KeyError if no section exists with this index
        """
        return self._sections[cy]

    def add_section(self, cy: int, section: numpy.ndarray):
        """Add a section. Overwrite if already exists
        :param cy: The section y index
        :param section: The Numpy array to add at this location
        :return:
        """
        assert isinstance(section, numpy.ndarray) and section.shape == (
            self.size_x,
            self.section_size_y,
            self.size_z,
        ), "section must be a numpy.ndarray of shape (16, 16, 16)"
        self._sections[cy] = section

    @staticmethod
    def _fix_slices(
        slices: Tuple[Union[int, slice], Union[int, slice], Union[int, slice]]
    ):
        if not isinstance(slices, tuple):
            raise IndexError(
                "only a tuple of length 3 containing ints and slices is allowed"
            )
        if len(slices) != 3:
            raise IndexError(
                f"Incorrect number of indices for PartialNDArray. Expected 3 got {len(slices)}"
            )
        x, y, z = slices
        if isinstance(y, slice):
            y = slice(y.start or 0, y.stop or 256, y.step)
        return x, y, z

    def _get_slices(
        self, slices: Tuple[Union[int, slice], Union[int, slice], Union[int, slice]]
    ) -> Generator[
        Tuple[int, Tuple[Union[int, slice], Union[int, slice], Union[int, slice]]],
        None,
        None,
    ]:
        slices = self._fix_slices(slices)
        if isinstance(slices[1], (int, numpy.integer)):
            yield slices[1] >> 4, (slices[0], slices[1] % 16, slices[2])
        elif isinstance(slices[1], slice):
            y_slice: slice = slices[1]
            start = y_slice.start
            stop = y_slice.stop
            step = y_slice.step
            cy_min = start >> 4
            cy_max = (stop - 1) >> 4
            ceil, floor = (
                (math.ceil, math.floor)
                if step is None or step >= 0
                else (math.floor, math.ceil)
            )
            for cy in range(cy_min, cy_max + 1):
                if step is None:
                    chunk_start = max(start, cy * 16)
                    chunk_stop = min(stop, (cy + 1) * 16)
                else:
                    chunk_start = min(
                        max(int(ceil((cy * 16 - start) / step)) * step + start, start),
                        (cy + 1) * 16,
                    )
                    chunk_stop = max(
                        min(
                            int(floor(((cy + 1) * 16 - 1 - start) / step)) * step
                            + start
                            + 1,
                            stop,
                        ),
                        cy * 16,
                    )
                    if chunk_start >= chunk_stop:
                        continue
                chunk_slice = slice(chunk_start - cy * 16, chunk_stop - cy * 16, step)
                yield cy, (slices[0], chunk_slice, slices[2])

    def __setitem__(
        self,
        slices: Tuple[Union[int, slice], Union[int, slice], Union[int, slice]],
        value: Union[int, numpy.integer, numpy.ndarray],
    ):
        if isinstance(value, (int, numpy.integer)):
            for cy, slices in self._get_slices(slices):
                self.get_create_section(cy)[slices] = value
        elif isinstance(value, numpy.ndarray):
            x, y, z = slices
            if isinstance(y, int):
                for cy, chunk_slices in self._get_slices(slices):
                    self.get_create_section(cy)[chunk_slices] = value
            elif isinstance(y, slice):
                y_min = y.start or 0
                for cy, chunk_slices in self._get_slices(slices):
                    chunk_y_start = cy * 16 + chunk_slices[1].start - y_min
                    chunk_y_stop = cy * 16 + chunk_slices[1].stop - y_min
                    if chunk_slices[1].step:
                        chunk_y_stop //= abs(chunk_slices[1].step)
                    self.get_create_section(cy)[chunk_slices] = value[
                        :, chunk_y_start:chunk_y_stop, :
                    ]
        else:
            raise ValueError(
                f"expected int or numpy.ndarray but got {value.__class__.__name__}"
            )

    @overload
    def __getitem__(self, slices: Tuple[int, int, int]) -> int:
        ...

    @overload
    def __getitem__(
        self, slices: Tuple[Union[int, slice], Union[int, slice], Union[int, slice]]
    ) -> numpy.ndarray:
        ...

    def __getitem__(self, slices):
        if all(isinstance(i, (int, numpy.integer)) for i in slices):
            cy, block = next(self._get_slices(slices))
            if cy in self:
                return self._sections[cy][block]
            else:
                return 0
        else:
            x, y, z = slices
            x_dim, z_dim = flat_16[x, z].shape
            if isinstance(y, slice):
                y_min = y.start or 0
                y_dim = (y.stop or 256) - y_min
                if y.step:
                    y_dim //= abs(y.step)
            else:
                y_min = y
                y_dim = 1
            array = numpy.zeros((x_dim, y_dim, z_dim), dtype=numpy.uint64)
            for cy, chunk_slices in self._get_slices(slices):
                if cy in self:
                    chunk_y = cy * 16 + chunk_slices[1].start - y_min
                    chunk_array: numpy.ndarray = self.get_section(cy)[chunk_slices]
                    array[:, chunk_y : chunk_y + chunk_array.shape[1], :] = chunk_array
            return array


if __name__ == "__main__":
    partial = PartialNDArray()
    print(partial[:, :, :].shape)  # (16, 256, 16)
    print(partial[:, -100:500, :].shape)  # (16, 600, 16)
    partial[:, :16, :] = 1
    print(partial[:, 0, :].shape)
    partial[:, 17, :] = partial[:, 0, :]
    print(partial.get_section(0))
    print(partial.get_section(1))

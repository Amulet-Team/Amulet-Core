from __future__ import annotations

from collections.abc import MutableMapping
from typing import Iterator, Union, Iterable

import numpy
from numpy.typing import ArrayLike


class SubChunkArrayContainer(MutableMapping[int, numpy.ndarray]):
    """A container of sub-chunk arrays"""

    def __init__(
        self,
        array_shape: tuple[int, int, int],
        default_array: Union[int, ArrayLike],
        arrays: Iterable[int, ArrayLike] = (),
    ):
        self._shape = array_shape
        self.default_array = default_array

        self._arrays = {}
        for cy, array in arrays:
            self[cy] = array

    @property
    def array_shape(self) -> tuple[int, int, int]:
        return self._shape

    @property
    def default_array(self) -> Union[int, numpy.ndarray]:
        return self._default_array

    @default_array.setter
    def default_array(self, default_array: Union[int, ArrayLike]):
        if isinstance(default_array, int):
            self._default_array = default_array
        else:
            self._default_array = self._cast_array(default_array)

    def _cast_array(self, array) -> numpy.ndarray:
        array = numpy.asarray(array)
        if not isinstance(array, numpy.ndarray):
            raise TypeError
        if array.shape != self._shape or array.dtype != numpy.uint32:
            raise ValueError
        return array

    def populate(self, cy: int):
        """Populate the section from the default array."""
        if cy in self._arrays:
            return
        default_array = self._default_array
        if isinstance(default_array, int):
            arr = numpy.full(self.array_shape, default_array, dtype=numpy.uint32)
        else:
            arr = numpy.array(default_array, dtype=numpy.uint32)
        self[cy] = arr

    def __setitem__(self, cy: int, array: ArrayLike):
        if not isinstance(cy, int):
            raise TypeError
        self._arrays[cy] = self._cast_array(array)

    def __delitem__(self, cy: int) -> None:
        del self._arrays[cy]

    def __getitem__(self, cy: int) -> numpy.ndarray:
        return self._arrays[cy]

    def __len__(self) -> int:
        return len(self._arrays)

    def __iter__(self) -> Iterator[int]:
        yield from self._arrays
from __future__ import annotations

from collections.abc import MutableMapping, Mapping
from typing import Iterator, Union, Iterable

import numpy
from numpy.typing import ArrayLike, NDArray

from amulet.utils.typed_property import TypedProperty


class SubChunkArrayContainer(MutableMapping[int, numpy.ndarray]):
    """A container of sub-chunk arrays"""

    _default_array: Union[int, numpy.ndarray]
    _arrays: dict[int, numpy.ndarray]

    def __init__(
        self,
        array_shape: tuple[int, int, int],
        default_array: Union[int, ArrayLike],
        arrays: Mapping[int, ArrayLike] | Iterable[tuple[int, ArrayLike]] = (),
    ) -> None:
        self._shape = array_shape
        self._set_default_array(default_array)

        self._arrays = {}
        if isinstance(arrays, Mapping):
            arrays = arrays.items()
        for cy, array in arrays:
            self[cy] = array

    @property
    def array_shape(self) -> tuple[int, int, int]:
        return self._shape

    @TypedProperty[Union[int, NDArray], Union[int, ArrayLike]]
    def default_array(self) -> Union[int, NDArray]:
        return self._default_array

    @default_array.setter
    def _set_default_array(self, default_array: Union[int, ArrayLike]) -> None:
        if isinstance(default_array, int):
            self._default_array = default_array
        else:
            self._default_array = self._cast_array(default_array)

    def _cast_array(self, array: ArrayLike) -> numpy.ndarray:
        array = numpy.asarray(array)
        if not isinstance(array, numpy.ndarray):
            raise TypeError
        if array.shape != self._shape or array.dtype != numpy.uint32:
            raise ValueError
        return array

    def populate(self, cy: int) -> None:
        """Populate the section from the default array."""
        if cy in self._arrays:
            return
        default_array = self._default_array
        if isinstance(default_array, int):
            arr = numpy.full(self.array_shape, default_array, dtype=numpy.uint32)
        else:
            arr = numpy.array(default_array, dtype=numpy.uint32)
        self[cy] = arr

    def __setitem__(self, cy: int, array: ArrayLike) -> None:
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

from typing import overload, Tuple, Union, Optional, Type, Dict
import numpy

from .base_partial_3d_array import BasePartial3DArray


class BoundedPartial3DArray(BasePartial3DArray):
    """This class should behave the same as a numpy array in all three axis
    but the data internally is stored in chunks to minimise memory usage.
    The array has a fixed size in all three axis much like a numpy array."""

    @classmethod
    def from_partial_array(
        cls,
        parent_array: "BasePartial3DArray",
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
            parent_array=parent_array,
        )

    @classmethod
    def from_sections(
        cls,
        dtype: Type[numpy.dtype],
        default_value: Union[int, bool],
        section_shape: Tuple[int, int, int],
        sections: Dict[int, numpy.ndarray],
        start: Tuple[int, int, int],
        stop: Tuple[int, int, int],
        step: Tuple[int, int, int],
    ):
        return cls(
            dtype, default_value, section_shape, start, stop, step, sections=sections,
        )

    def __init__(
            self,
            dtype: Type[numpy.dtype],
            default_value: Union[int, bool],
            section_shape: Tuple[int, int, int],
            start: Tuple[Optional[int], int, Optional[int]],
            stop: Tuple[Optional[int], int, Optional[int]],
            step: Tuple[Optional[int], Optional[int], Optional[int]],
            parent_array: Optional["BasePartial3DArray"] = None,
            sections: Optional[Dict[int, numpy.ndarray]] = None,
    ):
        assert isinstance(start[1], int) and isinstance(stop[1], int), "start[1] and stop[1] must both be ints."
        super().__init__(
            dtype,
            default_value,
            section_shape,
            start,
            stop,
            step,
            parent_array,
            sections
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
                y = item[1]
                if y >= 0:
                    y = self.start_y + y * self.step_y
                else:
                    y = self.stop_y + y * self.step_y

                if self.step_y > 0:
                    if not self.start_y <= y < self.stop_y:
                        raise Exception(f"Index {item[1]} is out of bounds for array length {self.size_y}")
                else:
                    y -= 1
                    if not self.start_y >= y > self.stop_y:
                        raise Exception(f"Index {item[1]} is out of bounds for array length {self.size_y}")

                cy = y // self.section_shape[1]
                if cy in self:
                    return int(
                        self._sections[cy][
                            (item[0], y % self.section_shape[1], item[2])
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

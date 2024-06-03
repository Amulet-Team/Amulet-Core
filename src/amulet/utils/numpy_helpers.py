from typing import Tuple, TypeVar
from collections.abc import Collection
import numpy

T = TypeVar("T")


def brute_sort_objects_no_hash(data: Collection[T]) -> Tuple[list[T], numpy.ndarray]:
    unique: list[T] = []
    inverse = numpy.zeros(dtype=numpy.uint32, shape=len(data))
    for i, d in enumerate(data):
        try:
            index = unique.index(d)
        except ValueError:
            index = len(unique)
            unique.append(d)
        inverse[i] = index

    return unique, numpy.array(inverse)

from typing import Tuple
import numpy


def brute_sort_objects_no_hash(data) -> Tuple[numpy.ndarray, numpy.ndarray]:
    unique = []
    inverse = numpy.zeros(dtype=numpy.uint32, shape=len(data))
    for i, d in enumerate(data):
        try:
            index = unique.index(d)
        except ValueError:
            index = len(unique)
            unique.append(d)
        inverse[i] = index

    unique_ = numpy.empty(len(unique), dtype=object)
    for index, obj in enumerate(unique):
        unique_[index] = obj

    return unique_, numpy.array(inverse)

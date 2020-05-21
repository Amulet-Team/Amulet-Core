from typing import Tuple, Sequence
import numpy


def brute_sort_objects(data) -> Tuple[numpy.ndarray, numpy.ndarray]:
    indexes = {}
    unique = []
    inverse = []
    index = 0
    for d in data:
        if d not in indexes:
            indexes[d] = index
            index += 1
            unique.append(d)
        inverse.append(indexes[d])

    unique_ = numpy.empty(len(unique), dtype=object)
    for index, obj in enumerate(unique):
        unique_[index] = obj

    return unique_, numpy.array(inverse)


def brute_sort_objects_no_hash(data) -> Tuple[numpy.ndarray, numpy.ndarray]:
    unique = []
    inverse = numpy.zeros(dtype=numpy.uint, shape=len(data))
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


def direct_object_array(array: Sequence) -> numpy.ndarray:
    np_array = numpy.empty(len(array), dtype=object)
    for index, obj in array:
        np_array[index] = object
    return np_array

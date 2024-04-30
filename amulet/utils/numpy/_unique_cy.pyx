# distutils: language = c++

cimport cython
from cython.operator cimport dereference
import numpy
cimport numpy
from libc.stdint cimport uint32_t
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map

numpy.import_array()


def unique_inverse(numpy.ndarray[numpy.uint32_t, ndim=1] array not None) -> tuple[numpy.ndarray, numpy.ndarray]:
    """Like numpy.unique(array, return_inverse=True) but 3-9 times faster.
    This only works on 1D uint32 arrays.
    The unique values are returned in the order they are found.
    """
    cdef size_t size = len(array)
    cdef numpy.ndarray[numpy.uint32_t, ndim=1] contiguous_array = numpy.ascontiguousarray(array, dtype=numpy.uint32)
    cdef numpy.ndarray[numpy.uint32_t, ndim=1] inverse = numpy.empty(size, dtype=numpy.uint32)
    cdef vector[uint32_t] unique_vector
    with nogil:
        unique_vector = _unique_inverse(<uint32_t*> contiguous_array.data, <uint32_t*> inverse.data, size)
    cdef uint32_t[::1] unique_memoryview = <uint32_t[:unique_vector.size():1]> unique_vector.data()
    cdef numpy.ndarray[numpy.uint32_t, ndim=1] unique = numpy.asarray(unique_memoryview).copy()
    return unique, inverse


@cython.boundscheck(False)
@cython.wraparound(False)
cdef vector[uint32_t] _unique_inverse(uint32_t* array, uint32_t* inverse, size_t size) noexcept nogil:
    cdef uint32_t index = 0
    cdef unordered_map[uint32_t, uint32_t] value_to_index
    cdef vector[uint32_t] unique

    cdef size_t i
    cdef uint32_t value
    cdef unordered_map[uint32_t, uint32_t].iterator it
    for i in range(size):
        value = array[i]
        it = value_to_index.find(value)
        if it == value_to_index.end():
            unique.push_back(value)
            inverse[i] = index
            value_to_index[value] = index
            index += 1
        else:
            inverse[i] = dereference(it).second
    return unique

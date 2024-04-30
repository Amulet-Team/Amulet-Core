import unittest
import numpy
from numpy.testing import assert_array_equal

from amulet.utils.numpy import unique_inverse


class TestUtilsNumpy(unittest.TestCase):
    def test_unique(self) -> None:
        for count_power in range(1, 13):
            count = 2 ** count_power
            for max_value_power in range(1, 20):
                max_value = 2 ** max_value_power
                values = numpy.random.randint(max_value, size=count, dtype=numpy.uint32)
                for length_power in range(1, 15):
                    length = 2 ** length_power
                    indexes = numpy.random.randint(count, size=length)
                    arr = values[indexes]

                    numpy_unique_values, numpy_index_array = numpy.unique(arr, return_inverse=True)
                    cy_unique_values, cy_index_array = unique_inverse(arr)
                    assert_array_equal(numpy_unique_values[numpy_index_array], cy_unique_values[cy_index_array])


if __name__ == "__main__":
    unittest.main()

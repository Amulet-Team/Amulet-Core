import unittest
import json
import numpy

from amulet.utils.world_utils import decode_long_array, encode_long_array
from tests.data.util import get_data_path


class LongArrayTestCase(unittest.TestCase):
    def test_longarray(self):
        with open(get_data_path("longarraytest.json")) as json_data:
            test_data = json.load(json_data)

        test_ran = False
        for test_entry in test_data["tests"]:
            test_ran = True
            block_array = numpy.asarray(test_entry["block_array"])
            long_array = numpy.asarray(test_entry["long_array"])
            palette_size = test_entry["palette_size"]

            numpy.testing.assert_array_equal(
                block_array,
                decode_long_array(
                    long_array, len(block_array), (palette_size - 1).bit_length()
                ),
            )

            numpy.testing.assert_array_equal(
                long_array,
                encode_long_array(block_array, (palette_size - 1).bit_length()),
            )

        # Make sure some test are ran in case the data file failed to load or has a wrong format.
        self.assertTrue(test_ran)

    def test_encode_decode(self):
        for signed in (False, True):
            for dense in (False, True):
                for bits_per_entry in range(4, 65):
                    for size in set(
                        [2**p for p in range(1, 13)] + list(range(100, 5000, 100))
                    ):
                        if signed:
                            arr = numpy.random.randint(
                                -(2**63), 2**63, size, dtype=numpy.int64
                            )
                        else:
                            arr = numpy.random.randint(
                                0, 2**64, size, dtype=numpy.uint64
                            )
                        arr >>= 64 - bits_per_entry

                        packed = encode_long_array(arr, bits_per_entry, dense)
                        arr2 = decode_long_array(
                            packed, len(arr), bits_per_entry, dense=dense, signed=signed
                        )
                        numpy.testing.assert_array_equal(
                            arr,
                            arr2,
                            f"Long array does not equal. Dense: {dense}, bits per entry: {bits_per_entry}, size: {size}",
                        )


if __name__ == "__main__":
    unittest.main()

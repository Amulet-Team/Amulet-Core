import unittest
import json
import numpy

from amulet.utils.world_utils import decode_long_array, encode_long_array
from tests.test_utils import get_data_path


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
                block_array, decode_long_array(long_array, len(block_array))
            )

            numpy.testing.assert_array_equal(long_array, encode_long_array(block_array))

        # Make sure some test are ran in case the data file failed to load or has a wrong format.
        self.assertTrue(test_ran)

    def test_encode_decode(self):
        for dense in (False, True):
            for bits_per_entry in range(4, 65):
                for size in [256, 4096]:
                    #     set(
                    #     [2**p for p in range(1, 13)] +
                    #     list(range(100, 5000, 100))
                    # ):
                    print(dense, bits_per_entry, size)
                    arr = numpy.arange(size) % (2 ** bits_per_entry)
                    packed = encode_long_array(arr, dense, bits_per_entry)
                    if not dense and bits_per_entry >= 11:
                        arr2 = decode_long_array(
                            packed, len(arr), dense, bits_per_entry
                        )
                    else:
                        arr2 = decode_long_array(packed, len(arr), dense)
                    numpy.testing.assert_array_equal(
                        arr,
                        arr2,
                        f"Long array does not equal. Dense: {dense}, bits per entry: {bits_per_entry}, size: {size}",
                    )


if __name__ == "__main__":
    unittest.main()

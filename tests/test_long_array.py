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


if __name__ == "__main__":
    unittest.main()

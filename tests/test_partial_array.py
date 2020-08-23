import unittest
import numpy
import random
import math

from amulet.api.partial_3d_array.util import get_sliced_array_size, sanitise_slice, unsanitise_slice
from amulet.api.partial_3d_array import UnboundedPartial3DArray, BoundedPartial3DArray


class PartialArrayTestCase(unittest.TestCase):
    def test_get_sliced_array_size(self):
        arr = numpy.arange(16)
        start_stop_values = list(range(-20, 20)) + [None]
        step_values = list(range(-5, 0)) + list(range(1, 6))

        for _ in range(50000):
            start = random.choice(start_stop_values)
            stop = random.choice(start_stop_values)
            step = random.choice(step_values)
            sub_arr = arr[slice(start, stop, step)]
            rsize = sub_arr.size
            size = get_sliced_array_size(start, stop, step, arr.size)
            if rsize != size:
                get_sliced_array_size(start, stop, step, arr.size)
            self.assertEqual(rsize, size, f"{start}, {stop}, {step} | {rsize} != {size} {sub_arr}")

    def test_unsanitise_slice(self):
        arr = numpy.arange(16)
        start_stop_values = list(range(-20, 20)) + [None]
        step_values = list(range(-5, 0)) + list(range(1, 6))

        for _ in range(50000):
            start = random.choice(start_stop_values)
            stop = random.choice(start_stop_values)
            step = random.choice(step_values)
            sub_arr = arr[slice(start, stop, step)]

            start2, stop2, step2 = sanitise_slice(start, stop, step, arr.size)
            start3, stop3, step3 = unsanitise_slice(start2, stop2, step2, arr.size)

            self.assertTrue(
                numpy.array_equal(
                    sub_arr,
                    arr[slice(start3, stop3, step3)]
                )
            )

    def test_access_unbounded_array(self):
        partial = UnboundedPartial3DArray(
            numpy.uint32,
            0,
            (4, 4, 4),
            (0, 16)
        )
        self.assertEqual(partial.shape, (4, math.inf, 4))
        self.assertIsInstance(partial[:, :, :], BoundedPartial3DArray)
        self.assertEqual(partial[:, :, :].shape, (4, 64, 4))
        self.assertEqual(partial[:, -100:500, :].shape, (4, 600, 4))
        self.assertEqual(partial[0, 0, 0], 0)
        self.assertEqual(partial[:, 0, :].shape, (4, 1, 4))
        self.assertEqual(partial[0, :, 0].shape, (1, 64, 1))

    @unittest.skip
    def test_set_unbounded_array(self):
        partial = UnboundedPartial3DArray(
            numpy.uint32,
            0,
            (4, 4, 4),
            (0, 16)
        )
        partial[:, :4, :] = 5
        self.assertEqual(tuple(partial.sections), (0,))
        self.assertTrue(numpy.all(partial.get_section(0) == 5))

        # partial[:, 17, :] = partial[:, 0, :]

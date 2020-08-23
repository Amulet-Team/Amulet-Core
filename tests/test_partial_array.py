import unittest
import numpy
import random
import math

from amulet.api.partial_3d_array.util import get_sliced_array_size, sanitise_slice, unsanitise_slice
from amulet.api.partial_3d_array import UnboundedPartial3DArray


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

    def test_array(self):
        class Partial3DArray16(UnboundedPartial3DArray):
            def __init__(self):
                super().__init__(
                    numpy.uint32,
                    0,
                    (16, 16, 16),
                    (0, 16)
                )

        partial = Partial3DArray16()
        self.assertEqual(partial.shape, (16, math.inf, 16))
        self.assertEqual(partial[:, :, :].shape, (16, 256, 16))
        self.assertEqual(partial[:, -100:500, :].shape, (16, 600, 16))
        self.assertEqual(partial[0, 0, 0], 0)
        self.assertEqual(partial[:, 0, :].shape, (16, 1, 16))
        self.assertEqual(partial[0, :, 0].shape, (1, 256, 1))

        # partial[:, :16, :] = 1

        # print(partial[:, 0, :].shape)

        # partial[:, 17, :] = partial[:, 0, :]

        # print(partial.get_section(0))
        # print(partial.get_section(1))

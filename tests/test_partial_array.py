import unittest
import numpy
import random

from amulet.api.partial_array.util import get_sliced_array_size, sanitise_slice, unsanitise_slice


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

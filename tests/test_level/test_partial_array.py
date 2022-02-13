import unittest
import numpy
import random
import math

from amulet.api.partial_3d_array.util import (
    get_sliced_array_size,
    sanitise_slice,
    unsanitise_slice,
)
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
            self.assertEqual(
                rsize, size, f"{start}, {stop}, {step} | {rsize} != {size} {sub_arr}"
            )

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
                numpy.array_equal(sub_arr, arr[slice(start3, stop3, step3)])
            )

    def test_access(self):
        section_size = 8
        section_count = 16
        partial = UnboundedPartial3DArray(
            numpy.uint32,
            0,
            (section_size, section_size, section_size),
            (0, section_count),
        )
        array = numpy.arange(
            (section_size**3) * section_count, dtype=partial.dtype
        ).reshape((section_size, section_size * section_count, section_size))
        for cy in range(section_count):
            partial.add_section(
                cy, array[:, cy * section_size : (cy + 1) * section_size, :]
            )

        # test __getitem__ shape
        self.assertEqual(partial.shape, (section_size, math.inf, section_size))
        self.assertIsInstance(partial[:, :, :], BoundedPartial3DArray)
        self.assertEqual(
            partial[:, :, :].shape,
            (section_size, section_size * section_count, section_size),
        )
        self.assertEqual(
            partial[:, -100:500, :].shape, (section_size, 600, section_size)
        )
        self.assertEqual(partial[:, 0, :].shape, (section_size, 1, section_size))
        self.assertEqual(partial[0, :, 0].shape, (1, section_size * section_count, 1))

        # test __getitem__ values
        for slices in (
            (0, 0, 0),
            (2, 30, 2),
            (-1, 30, -1),
        ):
            self.assertEqual(partial[slices], array[slices], str(slices))

        # test nested __getitem__ values
        for slices in (
            (slice(None), slice(None), slice(None)),
            (slice(1, -1), slice(1, 50), slice(1, -1)),
            (slice(-1, 1, -1), slice(50, 1, -1), slice(-1, 1, -1)),
            (slice(-1, 1, -2), slice(50, 1, -2), slice(-1, 1, -2)),
        ):
            self.assertEqual(partial[slices].shape, array[slices].shape)
            for slices2 in (
                (0, 0, 0),
                (-1, -1, -1),
            ):
                self.assertEqual(
                    partial[slices][slices2],
                    array[slices][slices2],
                    f"[{slices}][{slices2}]",
                )

        for slices in (
            (slice(None), slice(None), slice(None)),
            (slice(1, -1), slice(1, 50), slice(1, -1)),
            (slice(-1, 1, -1), slice(50, 1, -1), slice(-1, 1, -1)),
        ):
            self.assertEqual(partial[slices].shape, array[slices].shape)
            for slices2 in (
                (slice(None), slice(None), slice(None)),
                (slice(1, -1), slice(1, -1), slice(1, -1)),
                (slice(-1, 1, -1), slice(-1, 1, -1), slice(-1, 1, -1)),
            ):
                self.assertEqual(
                    partial[slices][slices2].shape,
                    array[slices][slices2].shape,
                    f"[{slices}][{slices2}]",
                )
                for slices3 in (
                    (0, 0, 0),
                    (-1, -1, -1),
                ):
                    self.assertEqual(
                        partial[slices][slices3],
                        array[slices][slices3],
                        f"[{slices}][{slices2}][{slices3}]",
                    )

    def test_set(self):
        section_size = 4
        section_count = 16
        partial = UnboundedPartial3DArray(
            numpy.uint32,
            0,
            (section_size, section_size, section_size),
            (0, section_count),
        )

        partial[:, :4, :] = 5
        self.assertTrue(numpy.all(numpy.asarray(partial[:, :4, :]) == 5))
        self.assertEqual(tuple(partial.sections), (0,))
        self.assertTrue(numpy.all(partial.get_section(0) == 5))
        partial[:, 2:6, :] = 10
        self.assertTrue(numpy.all(numpy.asarray(partial[:, :2, :]) == 5))
        self.assertTrue(numpy.all(numpy.asarray(partial[:, 2:6, :]) == 10))
        self.assertTrue(numpy.all(numpy.asarray(partial[:, 6:, :]) == 0))

        self.assertEqual(tuple(partial.sections), (0, 1))

        arange = numpy.arange(section_size**3 * 4).reshape(
            (section_size, section_size * 4, section_size)
        )
        partial[:, int(section_size * 4.5) : int(section_size * 8.5), :] = arange
        self.assertTrue(
            numpy.array_equal(
                partial[:, int(section_size * 4.5) : int(section_size * 8.5), :], arange
            )
        )

        partial[:, int(section_size * 8.5) : int(section_size * 12.5), :] = partial[
            :, int(section_size * 4.5) : int(section_size * 8.5), :
        ]
        self.assertTrue(
            numpy.array_equal(
                partial[:, int(section_size * 8.5) : int(section_size * 12.5), :],
                arange,
            )
        )
        self.assertTrue(
            numpy.array_equal(
                partial[:, int(section_size * 4.5) : int(section_size * 8.5), :],
                partial[:, int(section_size * 8.5) : int(section_size * 12.5), :],
            )
        )

    def test_eq(self):
        section_size = 4
        section_count = 16
        partial = UnboundedPartial3DArray(
            numpy.uint32,
            0,
            (section_size, section_size, section_size),
            (0, section_count),
        )
        bounded_partial = partial[:, :, :]
        self.assertTrue(numpy.all(bounded_partial == 0))
        self.assertTrue(numpy.all(0 == bounded_partial))
        self.assertFalse(numpy.all(bounded_partial == 10))
        self.assertFalse(numpy.all(10 == bounded_partial))
        self.assertFalse(numpy.any(bounded_partial == 10))
        self.assertFalse(numpy.any(10 == bounded_partial))

        arange = numpy.arange(section_size**3 * 4).reshape(
            (section_size, section_size * 4, section_size)
        )
        partial[:, int(section_size * 4.5) : int(section_size * 8.5), :] = arange

        self.assertTrue(
            numpy.all(
                arange
                == partial[:, int(section_size * 4.5) : int(section_size * 8.5), :]
            )
        )
        self.assertTrue(
            numpy.all(
                partial[:, int(section_size * 4.5) : int(section_size * 8.5), :]
                == arange
            )
        )

        self.assertFalse(
            numpy.all(
                arange
                == partial[:, int(section_size * 8.5) : int(section_size * 12.5), :]
            )
        )
        self.assertFalse(
            numpy.all(
                numpy.zeros((section_size, section_size * 4, section_size))
                == partial[:, int(section_size * 4.5) : int(section_size * 8.5), :]
            )
        )
        self.assertTrue(
            numpy.all(
                numpy.zeros((section_size, section_size * 4, section_size))
                == partial[:, int(section_size * 8.5) : int(section_size * 12.5), :]
            )
        )

    def test_eq_index(self):
        section_size = 4
        section_count = 16
        partial = UnboundedPartial3DArray(
            numpy.uint32,
            0,
            (section_size, section_size, section_size),
            (0, section_count),
        )
        bounded_partial = partial[:, :, :]
        self.assertTrue(numpy.all(bounded_partial == 0))

        arange = numpy.arange(section_size**3 * section_count).reshape(
            (section_size, section_size * section_count, section_size)
        )
        partial[:, :, :] = arange

        self.assertTrue(numpy.all(bounded_partial == arange))

        bounded_partial[numpy.asarray(bounded_partial) % 2 == 1] = 10
        arange[arange % 2 == 1] = 10

        self.assertTrue(numpy.all(bounded_partial == arange))

    def test_getitem_bool(self):
        array = numpy.arange(16**4, dtype=numpy.uint32).reshape((16, 16 * 16, 16))
        array[:, 128:, :] = 0
        partial_array = UnboundedPartial3DArray(
            numpy.uint32,
            0,
            (16, 16, 16),
            (0, 16),
            {sy: array[:, sy * 16 : (sy + 1) * 16, :].copy() for sy in range(8)},
        )

        array_slice = array[:, 0:200, :]
        bounded_partial_array = partial_array[:, 0:200, :]

        self.assertTrue(numpy.array_equal(array_slice, bounded_partial_array))

        bool_array = numpy.full(bounded_partial_array.shape, True, bool)
        self.assertTrue(
            numpy.array_equal(
                array_slice[bool_array], bounded_partial_array[bool_array]
            )
        )

        bool_array = numpy.random.choice([True, False], bounded_partial_array.shape)
        self.assertTrue(
            numpy.array_equal(
                array_slice[bool_array], bounded_partial_array[bool_array]
            )
        )

import unittest
import json
import numpy
import sys

from amulet.utils.world_utils import encode_long_array
from amulet.level.java.long_array import decode_long_array  # , encode_long_array
from data.util import get_data_path


class LongArrayTestCase(unittest.TestCase):
    def assertArrayEqual(self, a: numpy.ndarray, b: numpy.ndarray):
        self.assertEqual(a.dtype.kind, b.dtype.kind)
        self.assertEqual(a.dtype.itemsize, b.dtype.itemsize)
        numpy.testing.assert_array_equal(a, b)

    def test_decode_dtype(self):
        for bits_per_entry in range(1, 65):
            if 1 <= bits_per_entry <= 8:
                dtype = numpy.uint8
            elif 9 <= bits_per_entry <= 16:
                dtype = numpy.uint16
            elif 17 <= bits_per_entry <= 32:
                dtype = numpy.uint32
            elif 33 <= bits_per_entry <= 64:
                dtype = numpy.uint64
            else:
                raise RuntimeError
            with self.subTest(dtype=dtype, bits_per_entry=bits_per_entry):
                self.assertArrayEqual(
                    numpy.array([], dtype=dtype),
                    decode_long_array(
                        numpy.array([], dtype=numpy.int64), 0, bits_per_entry, False
                    ),
                )
                self.assertArrayEqual(
                    numpy.array([], dtype=dtype),
                    decode_long_array(
                        numpy.array([], dtype=numpy.int64), 0, bits_per_entry, True
                    ),
                )

    def test_decode_endianness(self) -> None:
        for dense in [True, False]:
            with self.subTest(dense=dense):
                self.assertArrayEqual(
                    numpy.array([1] * 64, dtype=numpy.uint8),
                    decode_long_array(
                        numpy.array([-1], dtype=numpy.int64), 64, 1, dense
                    ),
                )
                self.assertArrayEqual(
                    numpy.array([1] * 64, dtype=numpy.uint8),
                    decode_long_array(
                        numpy.array([2**64 - 1], dtype=numpy.uint64), 64, 1, dense
                    ),
                )
                if sys.byteorder == "little":
                    self.assertArrayEqual(
                        numpy.array([1] * 64, dtype=numpy.uint8),
                        decode_long_array(
                            numpy.array([-1], dtype=numpy.dtype("<i8")), 64, 1, dense
                        ),
                    )
                    self.assertArrayEqual(
                        numpy.array([1] * 64, dtype=numpy.uint8),
                        decode_long_array(
                            numpy.array([2**64 - 1], dtype=numpy.dtype("<u8")),
                            64,
                            1,
                            dense,
                        ),
                    )
                    arr = numpy.array([-1], dtype=numpy.dtype(">i8"))
                    with self.assertRaises(ValueError):
                        decode_long_array(arr, 64, 1, dense)
                    arr = numpy.array([2**64 - 1], dtype=numpy.dtype(">u8"))
                    with self.assertRaises(ValueError):
                        decode_long_array(arr, 64, 1, dense)
                else:
                    self.assertArrayEqual(
                        numpy.array([1] * 64, dtype=numpy.uint8),
                        decode_long_array(
                            numpy.array([-1], dtype=numpy.dtype(">i8")), 64, 1, dense
                        ),
                    )
                    self.assertArrayEqual(
                        numpy.array([1] * 64, dtype=numpy.uint8),
                        decode_long_array(
                            numpy.array([2**64 - 1], dtype=numpy.dtype(">u8")),
                            64,
                            1,
                            dense,
                        ),
                    )
                    arr = numpy.array([-1], dtype=numpy.dtype("<i8"))
                    with self.assertRaises(ValueError):
                        decode_long_array(arr, 64, 1, dense)
                    arr = numpy.array([2**64 - 1], dtype=numpy.dtype("<u8"))
                    with self.assertRaises(ValueError):
                        decode_long_array(arr, 64, 1, dense)
                for bit_size in (1, 2, 4):
                    for endianness in ("<", ">"):
                        with self.subTest(bit_size=bit_size, endianness=endianness):
                            arr = numpy.array(
                                [-1], dtype=numpy.dtype(f"{endianness}i{bit_size}")
                            )
                            with self.assertRaises(ValueError):
                                decode_long_array(arr, 64, 1, dense)
                            arr = numpy.array(
                                [2 ** (8 * bit_size) - 1],
                                dtype=numpy.dtype(f"{endianness}u{bit_size}"),
                            )
                            with self.assertRaises(ValueError):
                                decode_long_array(arr, 64, 1, dense)

    def test_decode(self):
        for dense in [True, False]:
            with self.subTest(dense=dense):
                self.assertArrayEqual(
                    numpy.array([0, 1, 0, 1, 0, 1], dtype=numpy.uint8),
                    decode_long_array(
                        numpy.array([0b101010], dtype=numpy.int64), 6, 1, dense
                    ),
                )
                self.assertArrayEqual(
                    numpy.array([0, 1, 0, 1], dtype=numpy.uint8),
                    decode_long_array(
                        numpy.array([0b101010], dtype=numpy.int64), 4, 1, dense
                    ),
                )
                self.assertArrayEqual(
                    numpy.array([0, 1, 0, 1, 0, 0], dtype=numpy.uint8),
                    decode_long_array(
                        numpy.array([0b1010], dtype=numpy.int64), 6, 1, dense
                    ),
                )

                self.assertArrayEqual(
                    numpy.array([0] * 32, dtype=numpy.uint8),
                    decode_long_array(
                        numpy.array([0], dtype=numpy.int64), 32, 1, dense
                    ),
                )
                self.assertArrayEqual(
                    numpy.array(
                        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3] * 2,
                        dtype=numpy.uint8,
                    ),
                    decode_long_array(
                        numpy.array([-4575586849434615808], dtype=numpy.int64),
                        32,
                        2,
                        dense,
                    ),
                )
                self.assertArrayEqual(
                    numpy.array(
                        [
                            *[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3],
                            *[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3],
                            *[1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3],
                            *[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3],
                        ],
                        dtype=numpy.uint8,
                    ),
                    decode_long_array(
                        numpy.array(
                            [-4575586849434615808, -4575586849434615807],
                            dtype=numpy.int64,
                        ),
                        64,
                        2,
                        dense,
                    ),
                )
                self.assertArrayEqual(
                    numpy.array([1, 2, 3] * 20, dtype=numpy.uint8),
                    decode_long_array(
                        numpy.array(
                            [-7027331075698876807, 65194966034315751], dtype=numpy.int64
                        ),
                        3 * 20,
                        2,
                        dense,
                    ),
                )
                self.assertArrayEqual(
                    numpy.array(
                        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3] * 4,
                        dtype=numpy.uint8,
                    ),
                    decode_long_array(
                        numpy.array(
                            [-4575586849434615808, -4575586849434615808],
                            dtype=numpy.int64,
                        ),
                        64,
                        2,
                        dense,
                    ),
                )

    def test_decode_overflow(self) -> None:
        self.assertArrayEqual(
            numpy.array([1, 2, 3, 4] * 10, dtype=numpy.uint8),
            decode_long_array(
                numpy.array(
                    [1788365664777214161, 79430520021295898], dtype=numpy.int64
                ),
                40,
                3,
                False,
            ),
        )
        self.assertArrayEqual(
            numpy.array([1, 2, 3, 4] * 10, dtype=numpy.uint8),
            decode_long_array(
                numpy.array(
                    [1788365664777214161, 39715260010647949], dtype=numpy.int64
                ),
                40,
                3,
                True,
            ),
        )


if __name__ == "__main__":
    unittest.main()

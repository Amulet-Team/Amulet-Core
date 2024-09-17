import unittest
import json
import numpy
import sys

from amulet.level.java.long_array import decode_long_array, encode_long_array
from data.util import get_data_path


class LongArrayTestCase(unittest.TestCase):
    def assertArrayEqual(self, a: numpy.ndarray, b: numpy.ndarray):
        self.assertEqual(a.dtype.kind, b.dtype.kind)
        self.assertEqual(a.dtype.itemsize, b.dtype.itemsize)
        numpy.testing.assert_array_equal(a, b)

    def test_decode_dtype(self) -> None:
        """Check that the decoded data type fits the required number of bits."""
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
        """Check that the native endianness is supported and non-native is rejected."""
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

    def test_decode(self) -> None:
        """Test decoding some values."""
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
        """Test decoding values that overflow into the next long."""
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

    def test_encode_dtype(self) -> None:
        """Test encoding data in different dtypes."""
        for dense in [True, False]:
            for bits_per_entry in range(1, 65):
                if 1 <= bits_per_entry <= 8:
                    dtype = numpy.uint8
                    signed_dtype = numpy.int8
                elif 9 <= bits_per_entry <= 16:
                    dtype = numpy.uint16
                    signed_dtype = numpy.int16
                elif 17 <= bits_per_entry <= 32:
                    dtype = numpy.uint32
                    signed_dtype = numpy.int32
                elif 33 <= bits_per_entry <= 64:
                    dtype = numpy.uint64
                    signed_dtype = numpy.int64
                else:
                    raise RuntimeError
                with self.subTest(
                    dense=dense, dtype=dtype, bits_per_entry=bits_per_entry
                ):
                    self.assertArrayEqual(
                        numpy.array([], dtype=numpy.uint64),
                        encode_long_array(numpy.array([], dtype=dtype), dense=dense),
                    )
                    arr = numpy.array([], dtype=signed_dtype)
                    with self.assertRaises(ValueError):
                        encode_long_array(arr, 0, dense=dense)

    def test_encode_endianness(self) -> None:
        """Test encoding different endiannesses."""
        native_endianness = "<" if sys.byteorder == "little" else ">"
        opposite_endianness = ">" if sys.byteorder == "little" else "<"
        for dense in [True, False]:
            for byte_count in (1, 2, 4, 8):
                dtype = f"{native_endianness}u{byte_count}"
                signed_dtype = f"{native_endianness}i{byte_count}"
                opposite_dtype = f"{opposite_endianness}u{byte_count}"
                opposite_signed_dtype = f"{opposite_endianness}i{byte_count}"
                with self.subTest(dense=dense, byte_count=byte_count):
                    self.assertArrayEqual(
                        numpy.array([], dtype=numpy.uint64),
                        encode_long_array(numpy.array([], dtype=dtype), dense=dense),
                    )
                    arr = numpy.array([], dtype=signed_dtype)
                    with self.assertRaises(ValueError):
                        encode_long_array(arr, dense=dense)
                    if byte_count == 1:
                        # Endianness does not exist for 1 byte ints
                        continue
                    arr = numpy.array([], dtype=opposite_dtype)
                    with self.assertRaises(ValueError):
                        encode_long_array(arr, dense=dense)
                    arr = numpy.array([], dtype=opposite_signed_dtype)
                    with self.assertRaises(ValueError):
                        encode_long_array(arr, dense=dense)

    def test_encode(self) -> None:
        """Test encoding some values."""
        for dense in [True, False]:
            with self.subTest(dense=dense):
                self.assertArrayEqual(
                    numpy.array([0b0], dtype=numpy.uint64),
                    encode_long_array(numpy.array([0], dtype=numpy.uint8), dense=dense),
                )
                self.assertArrayEqual(
                    numpy.array([0b1], dtype=numpy.uint64),
                    encode_long_array(numpy.array([1], dtype=numpy.uint8), dense=dense),
                )
                self.assertArrayEqual(
                    numpy.array([0b11], dtype=numpy.uint64),
                    encode_long_array(
                        numpy.array([1, 1], dtype=numpy.uint8), dense=dense
                    ),
                )
                self.assertArrayEqual(
                    numpy.array([0b101010], dtype=numpy.uint64),
                    encode_long_array(
                        numpy.array([0, 1, 0, 1, 0, 1], dtype=numpy.uint8), dense=dense
                    ),
                )
                self.assertArrayEqual(
                    numpy.array([0], dtype=numpy.uint64),
                    encode_long_array(
                        numpy.array([0] * 32, dtype=numpy.uint8), dense=dense
                    ),
                )
                self.assertArrayEqual(
                    numpy.array([-4575586849434615808], dtype=numpy.int64).astype(
                        numpy.uint64
                    ),
                    encode_long_array(
                        numpy.array(
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3] * 2,
                            dtype=numpy.uint8,
                        ),
                        dense=dense,
                    ),
                )
                self.assertArrayEqual(
                    numpy.array(
                        [-4575586849434615808, -4575586849434615807], dtype=numpy.int64
                    ).astype(numpy.uint64),
                    encode_long_array(
                        numpy.array(
                            [
                                *[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3],
                                *[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3],
                                *[1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3],
                                *[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3],
                            ],
                            dtype=numpy.uint8,
                        ),
                        dense=dense,
                    ),
                )
                self.assertArrayEqual(
                    numpy.array(
                        [-7027331075698876807, 65194966034315751], dtype=numpy.int64
                    ).astype(numpy.uint64),
                    encode_long_array(
                        numpy.array([1, 2, 3] * 20, dtype=numpy.uint8), dense=dense
                    ),
                )
                self.assertArrayEqual(
                    numpy.array(
                        [-4575586849434615808, -4575586849434615808], dtype=numpy.int64
                    ).astype(numpy.uint64),
                    encode_long_array(
                        numpy.array(
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3] * 4,
                            dtype=numpy.uint8,
                        ),
                        dense=dense,
                    ),
                )

    def test_encode_overflow(self) -> None:
        """Test encoding values that overflow into the next long."""
        self.assertArrayEqual(
            numpy.array(
                [1788365664777214161, 79430520021295898], dtype=numpy.int64
            ).astype(numpy.uint64),
            encode_long_array(
                numpy.array([1, 2, 3, 4] * 10, dtype=numpy.uint8), dense=False
            ),
        )
        self.assertArrayEqual(
            numpy.array(
                [1788365664777214161, 39715260010647949], dtype=numpy.int64
            ).astype(numpy.uint64),
            encode_long_array(
                numpy.array([1, 2, 3, 4] * 10, dtype=numpy.uint8), dense=True
            ),
        )

    def test_longarray(self) -> None:
        with open(get_data_path("longarraytest.json")) as json_data:
            test_data = json.load(json_data)
        tests = test_data["tests"]
        self.assertTrue(tests)

        for test_entry in tests:
            with self.subTest(test_entry=test_entry):
                block_array = numpy.asarray(test_entry["block_array"]).astype(
                    numpy.uint64
                )
                long_array = numpy.asarray(test_entry["long_array"]).astype(
                    numpy.uint64
                )
                palette_size = test_entry["palette_size"]

                numpy.testing.assert_array_equal(
                    block_array,
                    decode_long_array(
                        long_array,
                        len(block_array),
                        max(1, (palette_size - 1).bit_length()),
                    ),
                )

                numpy.testing.assert_array_equal(
                    long_array,
                    encode_long_array(
                        block_array, max(1, (palette_size - 1).bit_length())
                    ),
                )

    def test_encode_decode(self) -> None:
        for dense in (False, True):
            for bits_per_entry in range(4, 65):
                for size in set(
                    [2**p for p in range(1, 13)] + list(range(100, 5000, 100))
                ):
                    arr = numpy.random.randint(0, 2**64, size, dtype=numpy.uint64)
                    arr >>= 64 - bits_per_entry

                    with self.subTest(
                        dense=dense, bits_per_entry=bits_per_entry, size=size
                    ):
                        packed = encode_long_array(arr, bits_per_entry, dense)
                        arr2 = decode_long_array(
                            packed, len(arr), bits_per_entry, dense=dense
                        )
                        numpy.testing.assert_array_equal(
                            arr,
                            arr2,
                            f"Long array does not equal. Dense: {dense}, bits per entry: {bits_per_entry}, size: {size}",
                        )


if __name__ == "__main__":
    unittest.main()

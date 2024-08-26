import unittest
from weakref import ref
import numpy
import numpy.testing
from amulet.chunk_components.section_array_map import IndexArray3D
import faulthandler
faulthandler.enable()


class IndexArray3DTestCase(unittest.TestCase):
    def test_construct_shape(self) -> None:
        # Construct from shape
        array = IndexArray3D((1, 1, 1))
        self.assertEqual((1, 1, 1), array.shape)
        self.assertEqual(1, array.size)

        array = IndexArray3D((16, 16, 16))
        self.assertEqual((16, 16, 16), array.shape)
        self.assertEqual(16**3, array.size)

    def test_construct_shape_value(self) -> None:
        # Construct from shape and size
        array = IndexArray3D((16, 16, 16), 5)
        numpy.testing.assert_array_equal(
            numpy.full((16, 16, 16), 5, dtype=numpy.uint32),
            numpy.asarray(array)
        )

    def test_construct_self(self) -> None:
        # Construct from another IndexArray3D
        array = IndexArray3D((16, 16, 16), 5)
        array2 = IndexArray3D(array)
        numpy.testing.assert_array_equal(
            numpy.full((16, 16, 16), 5),
            numpy.asarray(array2)
        )

    def test_construct_buffer(self) -> None:
        # Construct from a numpy array
        np_arr = numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16))
        array = IndexArray3D(np_arr)
        self.assertEqual((16, 16, 16), array.shape)
        self.assertEqual(16 ** 3, array.size)
        numpy.testing.assert_array_equal(
            numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16)),
            numpy.asarray(array)
        )

    def test_construct_buffer_stride(self) -> None:
        # Construct from a numpy array with strides
        np_arr = numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16))[::2, ::2, ::2]
        array = IndexArray3D(np_arr)
        self.assertEqual((8, 8, 8), array.shape)
        self.assertEqual(8 ** 3, array.size)
        numpy.testing.assert_array_equal(
            numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16))[::2, ::2, ::2],
            numpy.asarray(array)
        )

    def test_np(self) -> None:
        array = IndexArray3D((16, 16, 16))
        np_array = numpy.array(array)
        self.assertEqual((16, 16, 16), np_array.shape)
        self.assertEqual(16 ** 3, np_array.size)

        array = IndexArray3D((16, 16, 16), 5)
        numpy.testing.assert_array_equal(
            numpy.full((16, 16, 16), 5),
            numpy.asarray(array)
        )
        numpy.asarray(array)[:] = 10
        numpy.testing.assert_array_equal(
            numpy.full((16, 16, 16), 10),
            numpy.asarray(array)
        )

    def test_delete(self) -> None:
        # asarray must hold a reference to array1.
        array1 = IndexArray3D((1, 1, 1))
        array1_ref = ref(array1)
        np_array1 = numpy.asarray(array1)
        del array1
        self.assertIsNot(None, array1_ref())

        # array creates a copy so array2 should be deleted.
        array2 = IndexArray3D((1, 1, 1))
        array2_ref = ref(array2)
        np_array2 = numpy.array(array2)
        del array2
        self.assertIs(None, array2_ref())


if __name__ == "__main__":
    unittest.main()

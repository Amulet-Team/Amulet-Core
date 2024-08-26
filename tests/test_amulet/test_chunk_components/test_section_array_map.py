import unittest
from weakref import ref
import numpy
import numpy.testing
from amulet.chunk_components.section_array_map import IndexArray3D, SectionArrayMap
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


class SectionArrayMapTestCase(unittest.TestCase):
    def test_construct_int(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        self.assertEqual((16, 16, 16), sections.array_shape)
        self.assertEqual(1, sections.default_array)

    def test_construct_array(self) -> None:
        sections = SectionArrayMap((16, 16, 16), IndexArray3D((16, 16, 16), 0))
        self.assertEqual((16, 16, 16), sections.array_shape)
        numpy.testing.assert_array_equal(numpy.zeros((16, 16, 16)), sections.default_array)

    def test_construct_np(self) -> None:
        sections = SectionArrayMap((16, 16, 16), numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16)))
        self.assertEqual((16, 16, 16), sections.array_shape)
        numpy.testing.assert_array_equal(numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16)), sections.default_array)

    def test_construct_errors(self) -> None:
        with self.assertRaises(ValueError):
            SectionArrayMap((16, 16, 16), numpy.arange(8**3, dtype=numpy.uint32).reshape((8, 8, 8)))
        with self.assertRaises(ValueError):
            SectionArrayMap((16, 16, 16), IndexArray3D((8, 8, 8)))

    def test_default_array(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        self.assertEqual(1, sections.default_array)
        sections.default_array = 2
        self.assertEqual(2, sections.default_array)
        sections.default_array = IndexArray3D((16, 16, 16), 0)
        numpy.testing.assert_array_equal(numpy.zeros((16, 16, 16)), sections.default_array)
        sections.default_array = numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16))
        numpy.testing.assert_array_equal(numpy.arange(16 ** 3, dtype=numpy.uint32).reshape((16, 16, 16)), sections.default_array)

    def test_populate(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        self.assertFalse(0 in sections)
        sections.populate(0)
        self.assertTrue(0 in sections)
        numpy.testing.assert_array_equal(
            numpy.ones((16, 16, 16), dtype=numpy.uint32),
            sections[0]
        )

        sections.default_array = numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16))
        sections.populate(1)
        numpy.testing.assert_array_equal(
            numpy.arange(16**3, dtype=numpy.uint32).reshape((16, 16, 16)),
            sections[1]
        )
        sections.populate(-1)
        numpy.testing.assert_array_equal(
            numpy.arange(16 ** 3, dtype=numpy.uint32).reshape((16, 16, 16)),
            sections[-1]
        )

    def test_getitem(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        with self.assertRaises(KeyError):
            arr = sections[0]
        with self.assertRaises(KeyError):
            arr = sections[-1]
        sections.populate(0)
        numpy.testing.assert_array_equal(
            numpy.ones((16, 16, 16), dtype=numpy.uint32),
            sections[0]
        )

    def test_setitem(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)

        sections[0] = numpy.full((16, 16, 16), 5, dtype=numpy.uint32)
        numpy.testing.assert_array_equal(
            numpy.full((16, 16, 16), 5, dtype=numpy.uint32),
            sections[0]
        )

        sections[1] = IndexArray3D((16, 16, 16), 10)
        numpy.testing.assert_array_equal(
            numpy.full((16, 16, 16), 10, dtype=numpy.uint32),
            sections[1]
        )

        sections[-1] = IndexArray3D((16, 16, 16), 10)
        numpy.testing.assert_array_equal(
            numpy.full((16, 16, 16), 10, dtype=numpy.uint32),
            sections[-1]
        )

    def test_delitem(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        sections.populate(0)
        sections.populate(1)
        self.assertEqual(2, len(sections))
        del sections[0]
        self.assertEqual(1, len(sections))
        sections.populate(-1)
        self.assertEqual(2, len(sections))
        del sections[-1]
        self.assertEqual(1, len(sections))

    def test_len(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        self.assertEqual(0, len(sections))
        sections.populate(0)
        self.assertEqual(1, len(sections))

    def test_iter(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        sections.populate(0)
        sections.populate(1)
        self.assertEqual({0, 1}, set(iter(sections)))

    def test_contains(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        sections.populate(0)
        self.assertIn(0, sections)
        self.assertNotIn(1, sections)
        self.assertNotIn(-1, sections)

    def test_keys(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        sections.populate(0)
        sections.populate(1)
        self.assertEqual({0, 1}, set(sections.keys()))
        self.assertEqual(2, len(list(sections.keys())))
        for k in sections.keys():
            self.assertIsInstance(k, int)

    def test_values(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        sections.populate(0)
        sections.populate(1)
        self.assertEqual(2, len(list(sections.values())))
        for v in sections.values():
            self.assertIsInstance(v, numpy.ndarray)
            numpy.testing.assert_array_equal(
                numpy.ones((16, 16, 16), dtype=numpy.uint32),
                v
            )

    def test_items(self) -> None:
        sections = SectionArrayMap((16, 16, 16), 1)
        sections.populate(0)
        sections.populate(1)
        self.assertEqual(2, len(list(sections.items())))
        for k, v in sections.items():
            self.assertIsInstance(k, int)
            self.assertIsInstance(v, numpy.ndarray)
            numpy.testing.assert_array_equal(
                numpy.ones((16, 16, 16), dtype=numpy.uint32),
                v
            )


if __name__ == "__main__":
    unittest.main()

import unittest
import numpy
import copy
import pickle

from amulet.api.chunk.biomes_v2 import Biomes


class BlockTestCase(unittest.TestCase):
    def test_init_none(self):
        biomes = Biomes()
        self.assertEqual(0, biomes.default_biome)
        self.assertIs(None, biomes.data_2d)
        self.assertEqual((), biomes.sub_chunks_3d)

        biomes = Biomes(default_biome=10)
        self.assertEqual(10, biomes.default_biome)
        self.assertIs(None, biomes.data_2d)
        self.assertEqual((), biomes.sub_chunks_3d)

    def test_default_biome(self):
        biomes = Biomes()
        biomes.default_biome = 10
        self.assertTrue(numpy.all(biomes.get_array_2d((16, 16)) == 10))

    def test_init_2d(self):
        with self.assertRaises(ValueError):
            Biomes(numpy.arange(4 ** 3).reshape((4, 4, 4)))

        biomes = Biomes(numpy.arange(4 ** 2).reshape((4, 4)))
        self.assertEqual(0, biomes.default_biome)
        numpy.testing.assert_array_equal(
            numpy.arange(4 ** 2).reshape((4, 4)), biomes.data_2d
        )
        self.assertEqual((), biomes.sub_chunks_3d)

    def test_2d(self):
        biomes = Biomes()
        self.assertIs(None, biomes.data_2d)
        with self.assertRaises(ValueError):
            biomes.data_2d = numpy.arange(4 ** 3).reshape((4, 4, 4))
        with self.assertRaises(TypeError):
            biomes.data_2d = "test"

        biomes.data_2d = numpy.arange(4 ** 2).reshape((4, 4))
        self.assertIsInstance(biomes.data_2d, numpy.ndarray)
        self.assertEqual((4, 4), biomes.shape_2d)
        numpy.testing.assert_array_equal(
            numpy.arange(4 ** 2).reshape((4, 4)), biomes.data_2d
        )

        biomes.data_2d = None
        self.assertIs(None, biomes.data_2d)
        self.assertIs(None, biomes.shape_2d)

        biomes.shape_2d = (4, 4)
        self.assertIsInstance(biomes.data_2d, numpy.ndarray)
        self.assertEqual((4, 4), biomes.shape_2d)

        biomes.data_2d = None

        self.assertIsInstance(biomes.get_array_2d((8, 8)), numpy.ndarray)
        self.assertEqual((8, 8), biomes.shape_2d)

    def test_init_3d(self):
        biomes = Biomes({1: numpy.arange(4 ** 3).reshape((4, 4, 4))})
        self.assertEqual(0, biomes.default_biome)
        self.assertEqual((1,), biomes.sub_chunks_3d)
        numpy.testing.assert_array_equal(
            numpy.arange(4 ** 3).reshape((4, 4, 4)), biomes.get_data_3d(1)
        )

    def _test_3d_empty(self, biomes):
        self.assertEqual((), biomes.sub_chunks_3d)
        self.assertFalse(biomes.has_array_3d(0))
        with self.assertRaises(KeyError):
            biomes.get_data_3d(0)
        with self.assertRaises(KeyError):
            biomes.get_shape_3d(0)
        with self.assertRaises(KeyError):
            biomes.delete_array_3d(0)

    def test_contains_3d(self):
        biomes = Biomes()

        self._test_3d_empty(biomes)

        biomes.get_array_3d(0, (16, 16, 16))
        biomes.set_shape_3d(1, (8, 8, 8))
        biomes.set_array_3d(2, numpy.arange(4 ** 3).reshape((4, 4, 4)))

        self.assertEqual((0, 1, 2), biomes.sub_chunks_3d)
        self.assertTrue(biomes.has_array_3d(0))
        self.assertTrue(biomes.has_array_3d(1))
        self.assertTrue(biomes.has_array_3d(2))
        self.assertFalse(biomes.has_array_3d(3))
        biomes.get_data_3d(0)
        biomes.get_data_3d(1)
        biomes.get_data_3d(2)
        with self.assertRaises(KeyError):
            biomes.get_data_3d(3)
        self.assertEqual((16, 16, 16), biomes.get_shape_3d(0))
        self.assertEqual((8, 8, 8), biomes.get_shape_3d(1))
        self.assertEqual((4, 4, 4), biomes.get_shape_3d(2))
        with self.assertRaises(KeyError):
            biomes.get_shape_3d(3)
        with self.assertRaises(KeyError):
            biomes.delete_array_3d(3)

        # delete the array
        biomes.delete_array_3d(0)
        biomes.delete_array_3d(1)
        biomes.delete_array_3d(2)
        self._test_3d_empty(biomes)

    def test_3d(self):
        biomes = Biomes()

        arr = biomes.get_array_3d(0, (16, 16, 16))
        self.assertEqual((16, 16, 16), arr.shape)
        self.assertTrue(numpy.all(arr == biomes.default_biome))

        arr2 = biomes.get_data_3d(0)
        self.assertIs(arr, arr2)
        self.assertEqual((16, 16, 16), arr2.shape)
        self.assertTrue(numpy.all(arr2 == biomes.default_biome))

        arr2 = biomes.get_array_3d(0, (16, 16, 16))
        self.assertIs(arr, arr2)
        self.assertEqual((16, 16, 16), arr2.shape)
        self.assertTrue(numpy.all(arr2 == biomes.default_biome))

        arr[:, :, :] = numpy.arange(16 ** 3).reshape((16, 16, 16))

        # test downscaling
        arr2 = biomes.get_array_3d(0, (4, 4, 4))
        self.assertEqual((4, 4, 4), arr2.shape)
        numpy.testing.assert_array_equal(
            numpy.arange(16 ** 3).reshape((16, 16, 16))[::4, ::4, ::4],
            arr2,
        )

        # test setting
        arr = numpy.arange(8).reshape((2, 2, 2))
        biomes.set_array_3d(0, arr)
        numpy.testing.assert_array_equal(
            numpy.arange(8).reshape((2, 2, 2)),
            biomes.get_data_3d(0),
        )
        self.assertIs(arr, biomes.get_data_3d(0))
        numpy.testing.assert_array_equal(
            numpy.arange(8).reshape((2, 2, 2)),
            biomes.get_array_3d(0, (2, 2, 2)),
        )
        self.assertIs(arr, biomes.get_array_3d(0, (2, 2, 2)))

        # test upscale
        numpy.testing.assert_array_equal(
            [
                [
                    [0, 0, 1, 1],
                    [0, 0, 1, 1],
                    [2, 2, 3, 3],
                    [2, 2, 3, 3],
                ],
                [
                    [0, 0, 1, 1],
                    [0, 0, 1, 1],
                    [2, 2, 3, 3],
                    [2, 2, 3, 3],
                ],
                [
                    [4, 4, 5, 5],
                    [4, 4, 5, 5],
                    [6, 6, 7, 7],
                    [6, 6, 7, 7],
                ],
                [
                    [4, 4, 5, 5],
                    [4, 4, 5, 5],
                    [6, 6, 7, 7],
                    [6, 6, 7, 7],
                ],
            ],
            biomes.get_array_3d(0, (4, 4, 4)),
        )

        # delete the array
        biomes.delete_array_3d(0)
        self._test_3d_empty(biomes)

    def test_convert(self):
        biomes = Biomes(numpy.arange(16).reshape((4, 4)))
        biomes.set_shape_3d(5, (4, 4, 4))

        biomes.convert_2d_to_3d()

        self.assertEqual((4, 1, 4), biomes.get_shape_3d(5))
        numpy.testing.assert_array_equal(
            numpy.arange(16).reshape((4, 1, 4)), biomes.get_data_3d(5)
        )

        biomes.get_data_3d(5)[:, :, :] = 10

        biomes.convert_3d_to_2d()

        self.assertTrue(numpy.all(biomes.data_2d == 10))

    def test_copy(self):
        biomes = Biomes()
        biomes.data_2d = numpy.arange(4 ** 2).reshape((4, 4))
        biomes.set_array_3d(0, numpy.arange(8 ** 3).reshape((8, 8, 8)))
        biomes.set_array_3d(1, numpy.arange(8 ** 3).reshape((8, 8, 8)) + 1)
        biomes.set_array_3d(2, numpy.arange(8 ** 3).reshape((8, 8, 8)) + 2)

        self.assertIsInstance(biomes, Biomes)

        biomes_copy = copy.copy(biomes)
        self.assertIsInstance(biomes_copy, Biomes)
        self.assertIs(biomes.data_2d, biomes_copy.data_2d)
        self.assertEqual(biomes.sub_chunks_3d, biomes_copy.sub_chunks_3d)
        for cy in biomes.sub_chunks_3d:
            self.assertIs(biomes.get_data_3d(cy), biomes_copy.get_data_3d(cy))

        biomes_deepcopy = copy.deepcopy(biomes)
        self.assertIsInstance(biomes_deepcopy, Biomes)
        self.assertIsNot(biomes.data_2d, biomes_deepcopy.data_2d)
        numpy.testing.assert_array_equal(biomes.data_2d, biomes_deepcopy.data_2d)
        self.assertEqual(biomes.sub_chunks_3d, biomes_deepcopy.sub_chunks_3d)
        for cy in biomes.sub_chunks_3d:
            self.assertIsNot(biomes.get_data_3d(cy), biomes_deepcopy.get_data_3d(cy))
            numpy.testing.assert_array_equal(
                biomes.get_data_3d(cy), biomes_deepcopy.get_data_3d(cy)
            )

    def test_pickle(self):
        biomes = Biomes()
        biomes.data_2d = numpy.arange(4 ** 2).reshape((4, 4))
        biomes.set_array_3d(0, numpy.arange(8 ** 3).reshape((8, 8, 8)))
        biomes.set_array_3d(1, numpy.arange(8 ** 3).reshape((8, 8, 8)) + 1)
        biomes.set_array_3d(2, numpy.arange(8 ** 3).reshape((8, 8, 8)) + 2)

        biomes_data = pickle.dumps(biomes)
        biomes2 = pickle.loads(biomes_data)

        self.assertIsInstance(biomes2, Biomes)
        self.assertIsNot(biomes.data_2d, biomes2.data_2d)
        numpy.testing.assert_array_equal(biomes.data_2d, biomes2.data_2d)
        self.assertEqual(biomes.sub_chunks_3d, biomes2.sub_chunks_3d)
        for cy in biomes.sub_chunks_3d:
            self.assertIsNot(biomes.get_data_3d(cy), biomes2.get_data_3d(cy))
            numpy.testing.assert_array_equal(
                biomes.get_data_3d(cy), biomes2.get_data_3d(cy)
            )


if __name__ == "__main__":
    unittest.main()

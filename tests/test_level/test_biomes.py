import unittest
import numpy
import copy

from amulet.api.chunk.biomes import Biomes


class BiomeTestCase(unittest.TestCase):
    def test_biomes(self):
        biomes = Biomes()
        biomes.convert_to_3d()
        self.assertEqual(biomes[:, :, :].shape, (4, 64, 4))

        arange = numpy.arange(16).reshape((4, 4))
        biomes[:, 0, :] = arange.reshape((4, 1, 4))

        biomes.convert_to_2d()
        self.assertTrue(numpy.array_equal(biomes[::4, ::4], arange))

    def test_copy(self):
        biomes = Biomes()
        self.assertIsInstance(biomes, Biomes)

        self.assertIsInstance(copy.deepcopy(biomes), Biomes)

        biomes.convert_to_2d()
        self.assertIsInstance(biomes.copy(), Biomes)
        self.assertIsInstance(copy.deepcopy(biomes), Biomes)

        biomes.convert_to_3d()
        self.assertIsInstance(biomes.copy(), Biomes)
        self.assertIsInstance(copy.deepcopy(biomes), Biomes)

import unittest
import numpy
from amulet.api.chunk.biomes import Biomes


class BlockTestCase(unittest.TestCase):
    def test_biomes(self):
        biomes = Biomes()
        self.assertEqual(biomes[:, :, :].shape, (4, 64, 4))

        arange = numpy.arange(16).reshape((4,4))
        biomes[:, 0, :] = arange.reshape((4, 1, 4))

        biomes.convert_to_2d()
        self.assertTrue(numpy.array_equal(biomes[::4, ::4], arange))

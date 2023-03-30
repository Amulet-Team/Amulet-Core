import unittest
import numpy
import numpy.testing
import copy

from amulet.api.chunk.biomes import Biomes, BiomesShape


class BiomeTestCase(unittest.TestCase):
    def test_biomes(self):
        biomes = Biomes()

        # Validate the null state
        self.assertIs(biomes.dimension, BiomesShape.ShapeNull)

        # Convert to 2D and validate the default the zero state
        biomes.convert_to_2d()
        self.assertIs(biomes.dimension, BiomesShape.Shape2D)
        arr = biomes[:, :]
        self.assertEqual(arr.shape, (16, 16))
        numpy.testing.assert_array_equal(arr, numpy.zeros((16, 16)))

        # Initialise 2D with arange
        biomes[:, :] = numpy.arange(16 * 16).reshape((16, 16))
        numpy.testing.assert_array_equal(
            biomes[:, :], numpy.arange(16 * 16).reshape((16, 16))
        )

        # Convert to 3D and check it is converted correctly.
        biomes.convert_to_3d()
        self.assertIs(biomes.dimension, BiomesShape.Shape3D)
        arr = biomes[:, :, :]
        self.assertEqual(arr.shape, (4, 64, 4))
        numpy.testing.assert_array_equal(
            arr,
            numpy.repeat(
                numpy.array(
                    [
                        [[0, 4, 8, 12]],
                        [[64, 68, 72, 76]],
                        [[128, 132, 136, 140]],
                        [[192, 196, 200, 204]],
                    ]
                ).reshape((4, 1, 4)),
                64,
                axis=1,
            ),
        )

        # Initialise 3D with arange
        biomes[:, :, :] = numpy.swapaxes(
            numpy.arange(4 * 64 * 4).reshape((64, 4, 4)), 0, 1
        )
        numpy.testing.assert_array_equal(
            biomes[:, :, :],
            numpy.swapaxes(numpy.arange(4 * 64 * 4).reshape((64, 4, 4)), 0, 1),
        )

        # Convert to 2D and check it is converted correctly.
        biomes.convert_to_2d()
        self.assertIs(biomes.dimension, BiomesShape.Shape2D)
        arr = biomes[:, :]
        self.assertEqual(arr.shape, (16, 16))
        numpy.testing.assert_array_equal(
            arr, numpy.kron(numpy.arange(4 * 4).reshape((4, 4)), numpy.ones((4, 4)))
        )

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

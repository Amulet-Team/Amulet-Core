import unittest
from amulet.biome import Biome
from amulet.palette import BiomePalette
from amulet.version import PlatformVersion, VersionNumber, VersionRange


plains = Biome(PlatformVersion("java", VersionNumber(3578)), "minecraft", "plains")
desert = Biome(PlatformVersion("java", VersionNumber(3578)), "minecraft", "desert")
forest = Biome(PlatformVersion("java", VersionNumber(3578)), "minecraft", "forest")


class BiomePaletteTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.palette = BiomePalette(
            VersionRange("java", VersionNumber(3578), VersionNumber(3578))
        )

        # Partially populate the manager
        self.palette.biome_to_index(plains)
        self.palette.biome_to_index(desert)
        self.palette.biome_to_index(forest)

    def test_get_item(self) -> None:
        self.assertEqual(plains, self.palette[0])
        self.assertEqual(desert, self.palette[1])
        self.assertEqual(forest, self.palette[2])
        with self.assertRaises(IndexError):
            self.palette[3]

    def test_index_to_biome(self) -> None:
        self.assertEqual(plains, self.palette.index_to_biome(0))
        self.assertEqual(desert, self.palette.index_to_biome(1))
        self.assertEqual(forest, self.palette.index_to_biome(2))
        with self.assertRaises(IndexError):
            self.palette.index_to_biome(3)

    def test_biome_to_index(self) -> None:
        self.assertEqual(0, self.palette.biome_to_index(plains))
        self.assertEqual(1, self.palette.biome_to_index(desert))
        self.assertEqual(2, self.palette.biome_to_index(forest))
        self.assertEqual(
            3,
            self.palette.biome_to_index(
                Biome(PlatformVersion("java", VersionNumber(3578)), "a", "b")
            ),
        )

    def test_len(self) -> None:
        palette = BiomePalette(
            VersionRange("java", VersionNumber(3578), VersionNumber(3578))
        )

        # Partially populate the manager
        palette.biome_to_index(plains)
        palette.biome_to_index(desert)
        palette.biome_to_index(forest)

        self.assertEqual(3, len(palette))

    def test_errors(self) -> None:
        with self.assertRaises(ValueError):
            self.palette.biome_to_index(
                Biome(PlatformVersion("java", VersionNumber(3579)), "a", "b")
            )
        with self.assertRaises(ValueError):
            self.palette.biome_to_index(
                Biome(PlatformVersion("java", VersionNumber(3577)), "a", "b")
            )


if __name__ == "__main__":
    unittest.main()

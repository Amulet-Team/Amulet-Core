import unittest

from amulet.biome import Biome
from amulet.game_version import JavaGameVersion


def get_test_biome() -> Biome:
    return Biome(JavaGameVersion(3578), "namespace", "basename")


def get_test_biome_variants() -> tuple[Biome, ...]:
    return (
        Biome(JavaGameVersion(3579), "namespace", "basename"),
        Biome(JavaGameVersion(3578), "namespace1", "basename"),
        Biome(JavaGameVersion(3578), "namespace", "basename1"),
    )


class BiomeTestCase(unittest.TestCase):
    def test_construct(self):
        biome = get_test_biome()
        self.assertEqual(JavaGameVersion(3578), biome.version)
        self.assertEqual("namespace", biome.namespace)
        self.assertEqual("basename", biome.base_name)

    def test_equal(self):
        self.assertEqual(get_test_biome(), get_test_biome())
        for biome in get_test_biome_variants():
            with self.subTest(repr(biome)):
                self.assertNotEqual(get_test_biome(), biome)

    def test_hash(self):
        self.assertEqual(hash(get_test_biome()), hash(get_test_biome()))
        for biome in get_test_biome_variants():
            with self.subTest(repr(biome)):
                self.assertNotEqual(hash(get_test_biome()), hash(biome))


if __name__ == "__main__":
    unittest.main()

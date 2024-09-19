import unittest

from amulet.biome import Biome
from amulet.version import VersionNumber


def get_test_biome() -> Biome:
    return Biome("java", VersionNumber(3578), "namespace", "basename")


def get_test_biome_variants() -> tuple[Biome, ...]:
    return (
        Biome("other", VersionNumber(3578), "namespace", "basename"),
        Biome("java", VersionNumber(3579), "namespace", "basename"),
        Biome("java", VersionNumber(3578), "namespace1", "basename"),
        Biome("java", VersionNumber(3578), "namespace", "basename1"),
    )


class BiomeTestCase(unittest.TestCase):
    def test_construct(self) -> None:
        biome = get_test_biome()
        self.assertEqual("java", biome.platform)
        self.assertEqual(VersionNumber(3578), biome.version)
        self.assertEqual("namespace", biome.namespace)
        self.assertEqual("basename", biome.base_name)

    def test_equal(self) -> None:
        self.assertEqual(get_test_biome(), get_test_biome())
        for biome in get_test_biome_variants():
            with self.subTest(repr(biome)):
                self.assertNotEqual(get_test_biome(), biome)

    def test_hash(self) -> None:
        self.assertEqual(hash(get_test_biome()), hash(get_test_biome()))
        for biome in get_test_biome_variants():
            with self.subTest(repr(biome)):
                self.assertNotEqual(hash(get_test_biome()), hash(biome))


if __name__ == "__main__":
    unittest.main()

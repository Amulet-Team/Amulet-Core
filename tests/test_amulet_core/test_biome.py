import unittest

from amulet.core.biome import Biome
from amulet.core.version import VersionNumber


class BiomeTestCase(unittest.TestCase):
    def test_cpp(self) -> None:
        from test_amulet_core.test_biome_ import get_tests

        for test_name, test in get_tests():
            with self.subTest(test_name):
                test()

    def test_construct(self) -> None:
        biome = Biome("java", VersionNumber(3578), "namespace", "basename")
        self.assertEqual("java", biome.platform)
        self.assertEqual(VersionNumber(3578), biome.version)
        self.assertEqual("namespace", biome.namespace)
        self.assertEqual("basename", biome.base_name)

    def test_equal(self) -> None:
        self.assertEqual(
            Biome("java", VersionNumber(3578), "namespace", "basename"),
            Biome("java", VersionNumber(3578), "namespace", "basename")
        )
        self.assertNotEqual(
            Biome("java", VersionNumber(3578), "namespace", "basename"),
            Biome("other", VersionNumber(3578), "namespace", "basename"),
        )
        self.assertNotEqual(
            Biome("java", VersionNumber(3578), "namespace", "basename"),
            Biome("java", VersionNumber(3579), "namespace", "basename"),
        )
        self.assertNotEqual(
            Biome("java", VersionNumber(3578), "namespace", "basename"),
            Biome("java", VersionNumber(3578), "namespace1", "basename"),
        )
        self.assertNotEqual(
            Biome("java", VersionNumber(3578), "namespace", "basename"),
            Biome("java", VersionNumber(3578), "namespace", "basename1"),
        )

    def test_compare(self) -> None:
        biome_1 = Biome("java", VersionNumber(1, 2, 3), "hello", "world")
        biome_2 = Biome("java", VersionNumber(1, 2, 3), "hello", "world")
        biome_3 = Biome("java_", VersionNumber(1, 2, 3), "hello", "world")
        biome_4 = Biome("java", VersionNumber(0, 2, 3), "hello", "world")
        biome_5 = Biome("java", VersionNumber(1, 3, 3), "hello", "world")
        biome_6 = Biome("java", VersionNumber(1, 2, 4), "hello", "world")
        biome_7 = Biome("java", VersionNumber(1, 2, 3), "hello_", "world")
        biome_8 = Biome("java", VersionNumber(1, 2, 3), "hello", "world_")

        self.assertEqual(biome_1, biome_2)
        self.assertGreaterEqual(biome_1, biome_2)
        self.assertLessEqual(biome_1, biome_2)

        self.assertLess(biome_1, biome_3)
        self.assertGreater(biome_1, biome_4)
        self.assertLess(biome_1, biome_5)
        self.assertLess(biome_1, biome_6)
        self.assertLess(biome_1, biome_7)
        self.assertLess(biome_1, biome_8)

    def test_hash(self) -> None:
        self.assertEqual(
            hash(Biome("java", VersionNumber(3578), "namespace", "basename")),
            hash(Biome("java", VersionNumber(3578), "namespace", "basename"))
        )
        self.assertNotEqual(
            hash(Biome("java", VersionNumber(3578), "namespace", "basename")),
            hash(Biome("other", VersionNumber(3578), "namespace", "basename")),
        )
        self.assertNotEqual(
            hash(Biome("java", VersionNumber(3578), "namespace", "basename")),
            hash(Biome("java", VersionNumber(3579), "namespace", "basename")),
        )
        self.assertNotEqual(
            hash(Biome("java", VersionNumber(3578), "namespace", "basename")),
            hash(Biome("java", VersionNumber(3578), "namespace1", "basename")),
        )
        self.assertNotEqual(
            hash(Biome("java", VersionNumber(3578), "namespace", "basename")),
            hash(Biome("java", VersionNumber(3578), "namespace", "basename1")),
        )


if __name__ == "__main__":
    unittest.main()

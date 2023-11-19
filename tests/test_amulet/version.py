from collections.abc import Sequence

from amulet.version import (
    VersionNumber,
    PlatformVersion,
    VersionRange,
)

import unittest


class VersionNumberTestCase(unittest.TestCase):
    def test_subclass(self) -> None:
        self.assertTrue(issubclass(VersionNumber, Sequence))
        self.assertIsInstance(VersionNumber(1, 0, 0), Sequence)
        self.assertIsInstance(VersionNumber(3578), Sequence)

    def test_equal(self) -> None:
        version_1 = VersionNumber(1, 0, 0)
        version_2 = VersionNumber(1, 2, 0)

        self.assertEqual(version_1, version_1)
        self.assertEqual(version_2, version_2)
        self.assertNotEqual(version_1, version_2)
        self.assertNotEqual(version_2, version_1)

        self.assertEqual(
            VersionNumber(1, 0, 0),
            VersionNumber(1, 0),
        )
        self.assertEqual(VersionNumber(1, 0, 0), VersionNumber(1))
        self.assertEqual(
            VersionNumber(1, 0),
            VersionNumber(1, 0, 0),
        )
        self.assertEqual(VersionNumber(1), VersionNumber(1, 0, 0))
        self.assertNotEqual(VersionNumber(1), 1)
        self.assertNotEqual(VersionNumber(1), (1,))

        self.assertEqual((1, 2, 3), tuple(VersionNumber(1, 2, 3)))

        self.assertEqual(VersionNumber(), VersionNumber(0, 0, 0))

    def test_hash(self) -> None:
        self.assertEqual(
            hash(VersionNumber(1, 0, 0)),
            hash(VersionNumber(1, 0, 0)),
        )
        self.assertEqual(
            hash(VersionNumber(1, 2, 0)),
            hash(VersionNumber(1, 2, 0)),
        )
        self.assertEqual(
            hash(VersionNumber(1, 2, 0)),
            hash(VersionNumber(1, 2)),
        )

    def test_compare(self) -> None:
        version_1 = VersionNumber(1, 0, 0)
        version_2 = VersionNumber(1, 2, 0)
        self.assertGreater(version_2, version_1)
        self.assertGreaterEqual(version_2, version_1)
        self.assertGreaterEqual(
            VersionNumber(1, 0, 0),
            VersionNumber(1, 0, 0),
        )
        self.assertGreaterEqual(
            VersionNumber(1, 0, 0),
            VersionNumber(1, 0),
        )
        self.assertGreaterEqual(VersionNumber(1, 0, 0), VersionNumber(1))
        self.assertGreaterEqual(
            VersionNumber(1, 0),
            VersionNumber(1, 0, 0),
        )
        self.assertGreaterEqual(VersionNumber(1), VersionNumber(1, 0, 0))
        self.assertLess(version_1, version_2)
        self.assertLessEqual(version_1, version_2)
        self.assertLessEqual(
            VersionNumber(1, 0, 0),
            VersionNumber(1, 0, 0),
        )
        self.assertLessEqual(
            VersionNumber(1, 0, 0),
            VersionNumber(1, 0),
        )
        self.assertLessEqual(VersionNumber(1, 0, 0), VersionNumber(1))
        self.assertLessEqual(
            VersionNumber(1, 0),
            VersionNumber(1, 0, 0),
        )
        self.assertLessEqual(VersionNumber(1), VersionNumber(1, 0, 0))


class PlatformVersionTestCase(unittest.TestCase):
    def test_equal(self) -> None:
        version_1 = PlatformVersion("platform1", VersionNumber(1))
        version_2 = PlatformVersion("platform1", VersionNumber(2))

        self.assertEqual(version_1, version_1)
        self.assertEqual(version_2, version_2)
        self.assertNotEqual(version_1, version_2)
        self.assertNotEqual(version_2, version_1)

        version_3 = PlatformVersion("platform2", VersionNumber(1))
        self.assertNotEqual(version_1, version_3)
        self.assertNotEqual(version_3, version_1)

    def test_hash(self) -> None:
        self.assertEqual(
            hash(PlatformVersion("platform1", VersionNumber(1))),
            hash(PlatformVersion("platform1", VersionNumber(1))),
        )
        self.assertEqual(
            hash(PlatformVersion("platform1", VersionNumber(2))),
            hash(PlatformVersion("platform1", VersionNumber(2))),
        )
        self.assertNotEqual(
            hash(PlatformVersion("platform1", VersionNumber(2))),
            hash(PlatformVersion("platform2", VersionNumber(2))),
        )

    def test_compare(self) -> None:
        version_1 = PlatformVersion("platform1", VersionNumber(1))
        version_2 = PlatformVersion("platform1", VersionNumber(2))
        self.assertGreater(version_2, version_1)
        self.assertGreaterEqual(version_2, version_1)
        self.assertLess(version_1, version_2)
        self.assertLessEqual(version_1, version_2)

    def test_errors(self) -> None:
        version_1 = PlatformVersion("platform1", VersionNumber(1))
        version_2 = PlatformVersion("platform2", VersionNumber(1))
        with self.assertRaises(ValueError):
            self.assertGreater(version_1, version_2)
        with self.assertRaises(ValueError):
            self.assertGreaterEqual(version_1, version_2)
        with self.assertRaises(ValueError):
            self.assertLess(version_1, version_2)
        with self.assertRaises(ValueError):
            self.assertLessEqual(version_1, version_2)


class PlatformVersionTestCase2(unittest.TestCase):
    def test_equal(self) -> None:
        version_1 = PlatformVersion("platform1", VersionNumber(1, 0, 0))
        version_2 = PlatformVersion("platform1", VersionNumber(1, 2, 0))

        self.assertEqual(version_1, version_1)
        self.assertEqual(version_2, version_2)
        self.assertNotEqual(version_1, version_2)
        self.assertNotEqual(version_2, version_1)

        self.assertEqual(
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
            PlatformVersion("platform1", VersionNumber(1, 0)),
        )
        self.assertEqual(
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
            PlatformVersion(
                "platform1",
                VersionNumber(
                    1,
                ),
            ),
        )
        self.assertEqual(
            PlatformVersion("platform1", VersionNumber(1, 0)),
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
        )
        self.assertEqual(
            PlatformVersion(
                "platform1",
                VersionNumber(
                    1,
                ),
            ),
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
        )

        version_3 = PlatformVersion("platform2", VersionNumber(1, 0, 0))
        self.assertNotEqual(version_1, version_3)
        self.assertNotEqual(version_3, version_1)

    def test_hash(self) -> None:
        self.assertEqual(
            hash(PlatformVersion("platform1", VersionNumber(1, 0, 0))),
            hash(PlatformVersion("platform1", VersionNumber(1, 0, 0))),
        )
        self.assertEqual(
            hash(PlatformVersion("platform1", VersionNumber(1, 2, 0))),
            hash(PlatformVersion("platform1", VersionNumber(1, 2, 0))),
        )
        self.assertNotEqual(
            hash(PlatformVersion("platform1", VersionNumber(1, 2, 0))),
            hash(PlatformVersion("platform2", VersionNumber(1, 2, 0))),
        )

    def test_compare(self) -> None:
        version_1 = PlatformVersion("platform1", VersionNumber(1, 0, 0))
        version_2 = PlatformVersion("platform1", VersionNumber(1, 2, 0))
        self.assertGreater(version_2, version_1)
        self.assertGreaterEqual(version_2, version_1)
        self.assertGreaterEqual(
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
        )
        self.assertGreaterEqual(
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
            PlatformVersion("platform1", VersionNumber(1, 0)),
        )
        self.assertGreaterEqual(
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
            PlatformVersion(
                "platform1",
                VersionNumber(
                    1,
                ),
            ),
        )
        self.assertGreaterEqual(
            PlatformVersion("platform1", VersionNumber(1, 0)),
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
        )
        self.assertGreaterEqual(
            PlatformVersion(
                "platform1",
                VersionNumber(
                    1,
                ),
            ),
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
        )
        self.assertLess(version_1, version_2)
        self.assertLessEqual(version_1, version_2)
        self.assertLessEqual(
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
        )
        self.assertLessEqual(
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
            PlatformVersion("platform1", VersionNumber(1, 0)),
        )
        self.assertLessEqual(
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
            PlatformVersion(
                "platform1",
                VersionNumber(
                    1,
                ),
            ),
        )
        self.assertLessEqual(
            PlatformVersion("platform1", VersionNumber(1, 0)),
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
        )
        self.assertLessEqual(
            PlatformVersion(
                "platform1",
                VersionNumber(
                    1,
                ),
            ),
            PlatformVersion("platform1", VersionNumber(1, 0, 0)),
        )

    def test_errors(self) -> None:
        version_1 = PlatformVersion("platform1", VersionNumber(1, 0, 0))
        version_2 = PlatformVersion("platform2", VersionNumber(1, 0, 0))
        with self.assertRaises(ValueError):
            self.assertGreater(version_1, version_2)
        with self.assertRaises(ValueError):
            self.assertGreaterEqual(version_1, version_2)
        with self.assertRaises(ValueError):
            self.assertLess(version_1, version_2)
        with self.assertRaises(ValueError):
            self.assertLessEqual(version_1, version_2)


class VersionRangeTestCase(unittest.TestCase):
    def test(self) -> None:
        version_range_1 = VersionRange("platform1", VersionNumber(1), VersionNumber(2))
        self.assertIn(PlatformVersion("platform1", VersionNumber(1)), version_range_1)
        self.assertIn(PlatformVersion("platform1", VersionNumber(2)), version_range_1)
        self.assertNotIn(
            PlatformVersion("platform1", VersionNumber(0)), version_range_1
        )
        self.assertNotIn(
            PlatformVersion("platform1", VersionNumber(3)), version_range_1
        )

        version_range_2 = VersionRange(
            "platform1",
            VersionNumber(1, 0, 0),
            VersionNumber(1, 2, 0),
        )
        self.assertIn(
            PlatformVersion("platform1", VersionNumber(1, 1, 0)), version_range_2
        )
        self.assertIn(PlatformVersion("platform1", VersionNumber(1)), version_range_2)
        self.assertNotIn(
            PlatformVersion("platform1", VersionNumber(0, 0, 0)), version_range_2
        )
        self.assertNotIn(
            PlatformVersion("platform1", VersionNumber(1, 3, 0)), version_range_2
        )
        self.assertNotIn(
            PlatformVersion("platform1", VersionNumber(2, 0, 0)), version_range_2
        )

    def test_errors(self) -> None:
        version_range_1 = VersionRange("platform1", VersionNumber(1), VersionNumber(2))
        with self.assertRaises(ValueError):
            PlatformVersion("platform2", VersionNumber(1)) in version_range_1

        version_range_2 = VersionRange(
            "platform1",
            VersionNumber(1, 0, 0),
            VersionNumber(1, 2, 0),
        )
        with self.assertRaises(ValueError):
            PlatformVersion("platform2", VersionNumber(1, 1, 0)) in version_range_2

        with self.assertRaises(ValueError):
            VersionRange("platform1", VersionNumber(2), VersionNumber(1))

        with self.assertRaises(ValueError):
            VersionRange(
                "platform1",
                VersionNumber(1, 2, 0),
                VersionNumber(1, 0, 0),
            )


if __name__ == "__main__":
    unittest.main()

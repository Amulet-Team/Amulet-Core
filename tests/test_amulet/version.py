from collections.abc import Sequence

from amulet.version import (
    VersionNumber,
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

        # Check negative numbers work
        self.assertLess(VersionNumber(1, -1), VersionNumber(1))
        self.assertLessEqual(VersionNumber(1, -1), VersionNumber(1))
        self.assertLess(VersionNumber(1, -1), VersionNumber(1, 0))
        self.assertLessEqual(VersionNumber(1, -1), VersionNumber(1, 0))
        self.assertGreater(VersionNumber(1), VersionNumber(1, -1))
        self.assertGreaterEqual(VersionNumber(1), VersionNumber(1, -1))
        self.assertGreater(VersionNumber(1, 0), VersionNumber(1, -1))
        self.assertGreaterEqual(VersionNumber(1, 0), VersionNumber(1, -1))

    def test_crop(self) -> None:
        self.assertEqual((1,), VersionNumber(1, 0, 0, 0, 0, 0, 0).cropped_version())

    def test_pad(self) -> None:
        with self.assertRaises(ValueError):
            VersionNumber(1, 2, 3).padded_version(-1)
        self.assertEqual((), VersionNumber(1, 2, 3).padded_version(0))
        self.assertEqual((1,), VersionNumber(1, 2, 3).padded_version(1))
        self.assertEqual((1, 2), VersionNumber(1, 2, 3).padded_version(2))
        self.assertEqual((1, 2, 3), VersionNumber(1, 2, 3).padded_version(3))
        self.assertEqual((1, 2, 3, 0), VersionNumber(1, 2, 3).padded_version(4))
        self.assertEqual((1, 2, 3, 0, 0), VersionNumber(1, 2, 3).padded_version(5))


class VersionRangeTestCase(unittest.TestCase):
    def test(self) -> None:
        version_range_1 = VersionRange("platform1", VersionNumber(1), VersionNumber(2))
        self.assertTrue(version_range_1.contains("platform1", VersionNumber(1)))
        self.assertTrue(version_range_1.contains("platform1", VersionNumber(2)))
        self.assertFalse(version_range_1.contains("platform1", VersionNumber(0)))
        self.assertFalse(version_range_1.contains("platform1", VersionNumber(3)))

        version_range_2 = VersionRange(
            "platform1",
            VersionNumber(1, 0, 0),
            VersionNumber(1, 2, 0),
        )
        self.assertTrue(version_range_2.contains("platform1", VersionNumber(1, 1, 0)))
        self.assertTrue(version_range_2.contains("platform1", VersionNumber(1)))
        self.assertFalse(version_range_2.contains("platform1", VersionNumber(0, 0, 0)))
        self.assertFalse(version_range_2.contains("platform1", VersionNumber(1, 3, 0)))
        self.assertFalse(version_range_2.contains("platform1", VersionNumber(2, 0, 0)))

    def test_errors(self) -> None:
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

from amulet.version import (
    AbstractVersion,
    DataVersion,
    SemanticVersion,
    VersionRange,
)

import unittest


class DataVersionTestCase(unittest.TestCase):
    def test_subclass(self):
        self.assertTrue(issubclass(DataVersion, AbstractVersion))
        self.assertIsInstance(DataVersion("platform1", 1), AbstractVersion)

    def test_equal(self):
        data_version_1 = DataVersion("platform1", 1)
        data_version_2 = DataVersion("platform1", 2)

        self.assertEqual(data_version_1, data_version_1)
        self.assertEqual(data_version_2, data_version_2)
        self.assertNotEqual(data_version_1, data_version_2)
        self.assertNotEqual(data_version_2, data_version_1)

    def test_hash(self):
        self.assertEqual(
            hash(DataVersion("platform1", 1)), hash(DataVersion("platform1", 1))
        )
        self.assertEqual(
            hash(DataVersion("platform1", 2)), hash(DataVersion("platform1", 2))
        )
        self.assertNotEqual(
            hash(DataVersion("platform1", 2)), hash(DataVersion("platform2", 2))
        )

    def test_compare(self):
        data_version_1 = DataVersion("platform1", 1)
        data_version_2 = DataVersion("platform1", 2)
        self.assertGreater(data_version_2, data_version_1)
        self.assertGreaterEqual(data_version_2, data_version_1)
        self.assertLess(data_version_1, data_version_2)
        self.assertLessEqual(data_version_1, data_version_2)

    def test_errors(self):
        data_version_1 = DataVersion("platform1", 1)
        data_version_2 = DataVersion("platform2", 1)
        with self.assertRaises(ValueError):
            self.assertEqual(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertNotEqual(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertGreater(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertGreaterEqual(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertLess(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertLessEqual(data_version_1, data_version_2)

    def test_compatible(self):
        data_version_1 = DataVersion("platform1", 1)
        data_version_2 = DataVersion("platform1", 2)
        data_version_3 = DataVersion("platform2", 1)
        data_version_4 = DataVersion("platform2", 2)

        self.assertTrue(data_version_1.is_compatible(data_version_2))
        self.assertTrue(data_version_2.is_compatible(data_version_1))
        self.assertTrue(data_version_3.is_compatible(data_version_4))
        self.assertTrue(data_version_4.is_compatible(data_version_3))
        self.assertFalse(data_version_1.is_compatible(data_version_4))
        self.assertFalse(data_version_2.is_compatible(data_version_3))
        self.assertFalse(data_version_3.is_compatible(data_version_2))
        self.assertFalse(data_version_4.is_compatible(data_version_1))


class SemanticVersionTestCase(unittest.TestCase):
    def test_subclass(self):
        self.assertTrue(issubclass(SemanticVersion, AbstractVersion))
        self.assertIsInstance(SemanticVersion("platform1", (1, 0, 0)), AbstractVersion)

    def test_equal(self):
        data_version_1 = SemanticVersion("platform1", (1, 0, 0))
        data_version_2 = SemanticVersion("platform1", (1, 2, 0))

        self.assertEqual(data_version_1, data_version_1)
        self.assertEqual(data_version_2, data_version_2)
        self.assertNotEqual(data_version_1, data_version_2)
        self.assertNotEqual(data_version_2, data_version_1)

        self.assertEqual(
            SemanticVersion("platform1", (1, 0, 0)),
            SemanticVersion("platform1", (1, 0)),
        )
        self.assertEqual(
            SemanticVersion("platform1", (1, 0, 0)), SemanticVersion("platform1", (1,))
        )
        self.assertEqual(
            SemanticVersion("platform1", (1, 0)),
            SemanticVersion("platform1", (1, 0, 0)),
        )
        self.assertEqual(
            SemanticVersion("platform1", (1,)), SemanticVersion("platform1", (1, 0, 0))
        )

    def test_hash(self):
        self.assertEqual(
            hash(SemanticVersion("platform1", (1, 0, 0))),
            hash(SemanticVersion("platform1", (1, 0, 0))),
        )
        self.assertEqual(
            hash(SemanticVersion("platform1", (1, 2, 0))),
            hash(SemanticVersion("platform1", (1, 2, 0))),
        )
        self.assertNotEqual(
            hash(SemanticVersion("platform1", (1, 2, 0))),
            hash(SemanticVersion("platform2", (1, 2, 0))),
        )

    def test_compare(self):
        data_version_1 = SemanticVersion("platform1", (1, 0, 0))
        data_version_2 = SemanticVersion("platform1", (1, 2, 0))
        self.assertGreater(data_version_2, data_version_1)
        self.assertGreaterEqual(data_version_2, data_version_1)
        self.assertGreaterEqual(
            SemanticVersion("platform1", (1, 0, 0)),
            SemanticVersion("platform1", (1, 0, 0)),
        )
        self.assertGreaterEqual(
            SemanticVersion("platform1", (1, 0, 0)),
            SemanticVersion("platform1", (1, 0)),
        )
        self.assertGreaterEqual(
            SemanticVersion("platform1", (1, 0, 0)), SemanticVersion("platform1", (1,))
        )
        self.assertGreaterEqual(
            SemanticVersion("platform1", (1, 0)),
            SemanticVersion("platform1", (1, 0, 0)),
        )
        self.assertGreaterEqual(
            SemanticVersion("platform1", (1,)), SemanticVersion("platform1", (1, 0, 0))
        )
        self.assertLess(data_version_1, data_version_2)
        self.assertLessEqual(data_version_1, data_version_2)
        self.assertLessEqual(
            SemanticVersion("platform1", (1, 0, 0)),
            SemanticVersion("platform1", (1, 0, 0)),
        )
        self.assertLessEqual(
            SemanticVersion("platform1", (1, 0, 0)),
            SemanticVersion("platform1", (1, 0)),
        )
        self.assertLessEqual(
            SemanticVersion("platform1", (1, 0, 0)), SemanticVersion("platform1", (1,))
        )
        self.assertLessEqual(
            SemanticVersion("platform1", (1, 0)),
            SemanticVersion("platform1", (1, 0, 0)),
        )
        self.assertLessEqual(
            SemanticVersion("platform1", (1,)), SemanticVersion("platform1", (1, 0, 0))
        )

    def test_errors(self):
        data_version_1 = SemanticVersion("platform1", (1, 0, 0))
        data_version_2 = SemanticVersion("platform2", (1, 0, 0))
        with self.assertRaises(ValueError):
            self.assertEqual(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertNotEqual(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertGreater(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertGreaterEqual(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertLess(data_version_1, data_version_2)
        with self.assertRaises(ValueError):
            self.assertLessEqual(data_version_1, data_version_2)

    def test_compatible(self):
        data_version_1 = SemanticVersion("platform1", (1, 0, 0))
        data_version_2 = SemanticVersion("platform1", (1, 2, 0))
        data_version_3 = SemanticVersion("platform2", (1, 0, 0))
        data_version_4 = SemanticVersion("platform2", (1, 2, 0))

        self.assertTrue(data_version_1.is_compatible(data_version_2))
        self.assertTrue(data_version_2.is_compatible(data_version_1))
        self.assertTrue(data_version_3.is_compatible(data_version_4))
        self.assertTrue(data_version_4.is_compatible(data_version_3))
        self.assertFalse(data_version_1.is_compatible(data_version_4))
        self.assertFalse(data_version_2.is_compatible(data_version_3))
        self.assertFalse(data_version_3.is_compatible(data_version_2))
        self.assertFalse(data_version_4.is_compatible(data_version_1))


class VersionRangeTestCase(unittest.TestCase):
    def test(self):
        data_version_range = VersionRange(
            DataVersion("platform1", 1), DataVersion("platform1", 2)
        )
        self.assertIn(DataVersion("platform1", 1), data_version_range)
        self.assertIn(DataVersion("platform1", 2), data_version_range)
        self.assertNotIn(DataVersion("platform1", 0), data_version_range)
        self.assertNotIn(DataVersion("platform1", 3), data_version_range)

        semantic_version_range = VersionRange(
            SemanticVersion("platform1", (1, 0, 0)),
            SemanticVersion("platform1", (1, 2, 0)),
        )
        self.assertIn(SemanticVersion("platform1", (1, 1, 0)), semantic_version_range)
        self.assertIn(SemanticVersion("platform1", (1,)), semantic_version_range)
        self.assertNotIn(
            SemanticVersion("platform1", (0, 0, 0)), semantic_version_range
        )
        self.assertNotIn(
            SemanticVersion("platform1", (1, 3, 0)), semantic_version_range
        )
        self.assertNotIn(
            SemanticVersion("platform1", (2, 0, 0)), semantic_version_range
        )

    def test_errors(self):
        data_version_range = VersionRange(
            DataVersion("platform1", 1), DataVersion("platform1", 2)
        )
        with self.assertRaises(ValueError):
            DataVersion("platform2", 1) in data_version_range

        semantic_version_range = VersionRange(
            SemanticVersion("platform1", (1, 0, 0)),
            SemanticVersion("platform1", (1, 2, 0)),
        )
        with self.assertRaises(ValueError):
            SemanticVersion("platform2", (1, 1, 0)) in semantic_version_range

        with self.assertRaises(ValueError):
            VersionRange(DataVersion("platform1", 1), DataVersion("platform2", 1))

        with self.assertRaises(ValueError):
            VersionRange(DataVersion("platform1", 2), DataVersion("platform1", 1))

        with self.assertRaises(ValueError):
            VersionRange(
                SemanticVersion("platform1", (1, 0, 0)),
                SemanticVersion("platform2", (1, 2, 0)),
            )

        with self.assertRaises(ValueError):
            VersionRange(
                SemanticVersion("platform1", (1, 2, 0)),
                SemanticVersion("platform1", (1, 0, 0)),
            )

        with self.assertRaises(TypeError):
            VersionRange(
                SemanticVersion("platform1", (1, 0, 0)), DataVersion("platform1", 1)
            )

        with self.assertRaises(TypeError):
            SemanticVersion("platform1", (1, 0, 0)) in data_version_range

        with self.assertRaises(TypeError):
            DataVersion("platform1", 1) in semantic_version_range


if __name__ == "__main__":
    unittest.main()

import unittest

from amulet.core.selection import SelectionBoxGroup, SelectionBox


class SelectionBoxTestCase(unittest.TestCase):
    def test_cpp(self) -> None:
        from test_amulet_core.test_selection.test_selection_box_ import get_tests

        for test in get_tests():
            with self.subTest(test=test.__name__):
                test()

    def test_attrs(self) -> None:
        box = SelectionBox(0, 1, 2, 3, 4, 5)

        self.assertIsInstance(box.min_x, int)
        self.assertIsInstance(box.min_y, int)
        self.assertIsInstance(box.min_z, int)
        self.assertEqual(0, box.min_x)
        self.assertEqual(1, box.min_y)
        self.assertEqual(2, box.min_z)

        self.assertIsInstance(box.max_x, int)
        self.assertIsInstance(box.max_y, int)
        self.assertIsInstance(box.max_z, int)
        self.assertEqual(3, box.max_x)
        self.assertEqual(5, box.max_y)
        self.assertEqual(7, box.max_z)

        self.assertIsInstance(box.min, tuple)
        self.assertIsInstance(box.max, tuple)
        self.assertEqual((0, 1, 2), box.min)
        self.assertEqual((3, 5, 7), box.max)

        self.assertIsInstance(box.size_x, int)
        self.assertIsInstance(box.size_y, int)
        self.assertIsInstance(box.size_z, int)
        self.assertEqual(3, box.size_x)
        self.assertEqual(4, box.size_y)
        self.assertEqual(5, box.size_z)

        self.assertIsInstance(box.shape, tuple)
        self.assertEqual((3, 4, 5), box.shape)

        self.assertIsInstance(box.volume, int)
        self.assertEqual(3 * 4 * 5, box.volume)

    def test_equals(self) -> None:
        self.assertEqual(
            SelectionBox((0, 0, 0), (5, 5, 5)), SelectionBox((0, 0, 0), (5, 5, 5))
        )
        self.assertEqual(
            SelectionBox((5, 5, 5), (0, 0, 0)), SelectionBox((5, 5, 5), (0, 0, 0))
        )
        self.assertEqual(
            SelectionBox((0, 0, 0), (5, 5, 5)), SelectionBox((5, 5, 5), (0, 0, 0))
        )
        self.assertEqual(
            SelectionBox((1, 2, 3), (2, 3, 4)),
            SelectionBox(1, 2, 3, 1, 1, 1),
        )
        self.assertEqual(
            SelectionBox((2, 3, 4), (1, 2, 3)),
            SelectionBox(1, 2, 3, 1, 1, 1),
        )
        for box in (
            SelectionBox(1, 0, 0, 1, 1, 1),
            SelectionBox(0, 1, 0, 1, 1, 1),
            SelectionBox(0, 0, 1, 1, 1, 1),
            SelectionBox(0, 0, 0, 2, 1, 1),
            SelectionBox(0, 0, 0, 1, 2, 1),
            SelectionBox(0, 0, 0, 1, 1, 2),
        ):
            with self.subTest(box=box):
                self.assertNotEqual(
                    SelectionBox(0, 0, 0, 1, 1, 1),
                    box,
                )

    def test_contains(self) -> None:
        box = SelectionBox(0, 1, 2, 3, 4, 5)
        self.assertTrue(box.contains_block(0, 1, 2))
        self.assertFalse(box.contains_block(3, 3, 3))
        self.assertTrue(box.contains_point(0, 1, 2))
        self.assertTrue(box.contains_point(3, 3, 3))
        self.assertTrue(box.contains_point(3.0, 3.0, 3.0))
        self.assertFalse(box.contains_point(3.1, 3.1, 3.1))

        box = SelectionBox(-1, -1, -1, 2, 2, 2)
        self.assertTrue(box.contains_block(-1, -1, -1))
        self.assertTrue(box.contains_block(0, 0, 0))
        self.assertFalse(box.contains_block(1, 1, 1))

        self.assertTrue(box.contains_box(SelectionBox(0, 0, 0, 1, 1, 1)))
        self.assertFalse(box.contains_box(SelectionBox(0, 0, 0, 2, 2, 2)))
        self.assertFalse(box.contains_box(SelectionBox(1, 1, 1, 1, 1, 1)))

        self.assertTrue(box.intersects(SelectionBox(0, 0, 0, 1, 1, 1)))
        self.assertTrue(box.intersects(SelectionBox(0, 0, 0, 2, 2, 2)))
        self.assertFalse(box.intersects(SelectionBox(1, 1, 1, 1, 1, 1)))

        self.assertTrue(
            box.intersects(SelectionBoxGroup([SelectionBox(0, 0, 0, 1, 1, 1)]))
        )
        self.assertTrue(
            box.intersects(SelectionBoxGroup([SelectionBox(0, 0, 0, 2, 2, 2)]))
        )
        self.assertFalse(
            box.intersects(SelectionBoxGroup([SelectionBox(1, 1, 1, 1, 1, 1)]))
        )

        self.assertTrue(box.touches_or_intersects(SelectionBox(0, 0, 0, 1, 1, 1)))
        self.assertTrue(box.touches_or_intersects(SelectionBox(0, 0, 0, 2, 2, 2)))
        self.assertTrue(box.touches_or_intersects(SelectionBox(1, 1, 1, 1, 1, 1)))

        self.assertFalse(box.touches(SelectionBox(0, 0, 0, 1, 1, 1)))
        self.assertFalse(box.touches(SelectionBox(0, 0, 0, 2, 2, 2)))
        self.assertTrue(box.touches(SelectionBox(1, 1, 1, 1, 1, 1)))

    def test_transform(self) -> None:
        self.assertEqual(
            SelectionBox(2, 3, 4, 1, 1, 1),
            SelectionBox(1, 1, 1, 1, 1, 1).translate(1, 2, 3),
        )
        self.assertEqual(
            SelectionBox(0, -1, -2, 1, 1, 1),
            SelectionBox(1, 1, 1, 1, 1, 1).translate(-1, -2, -3),
        )

    def test_single_block_box(self) -> None:
        box_1 = SelectionBox((0, 0, 0), (1, 1, 2))

        self.assertEqual((1, 1, 2), box_1.shape)
        # self.assertEqual(2, len([x for x in box_1.blocks]))

        self.assertTrue(box_1.contains_block(0, 0, 0))
        self.assertFalse(box_1.contains_block(1, 1, 2))


if __name__ == "__main__":
    unittest.main()

import unittest
from amulet.api.selection import SelectionGroup, SelectionBox


class SelectionTestCase(unittest.TestCase):
    def test_equals(self):
        box_1 = SelectionBox((0, 0, 0), (5, 5, 5))
        box_2 = SelectionBox((5, 5, 5), (0, 0, 0))
        self.assertEqual(box_1, box_2)

    def test_intersects(self):
        box_1 = SelectionBox((0, 0, 0), (5, 5, 5))
        box_2 = SelectionBox((4, 4, 4), (10, 10, 10))
        box_3 = SelectionBox((5, 5, 5), (10, 10, 10))
        box_4 = SelectionBox((1, 20, 1), (4, 25, 4))

        self.assertTrue(box_1.intersects(box_2))
        self.assertTrue(box_2.intersects(box_1))
        self.assertFalse(box_1.intersects(box_3))
        self.assertFalse(box_3.intersects(box_1))
        self.assertFalse(box_1.intersects(box_4))
        self.assertFalse(box_4.intersects(box_1))

    def test_is_contiguous(self):
        box = SelectionBox((0, 0, 0), (5, 5, 5))

        self.assertTrue(SelectionGroup(box).is_contiguous)
        # top corner
        self.assertTrue(
            SelectionGroup((box, SelectionBox((5, 5, 5), (10, 10, 10)))).is_contiguous
        )
        # bottom corner
        self.assertTrue(
            SelectionGroup((box, SelectionBox((-5, -5, -5), (0, 0, 0)))).is_contiguous
        )
        # top face
        self.assertTrue(
            SelectionGroup((box, SelectionBox((0, 5, 0), (5, 10, 5)))).is_contiguous
        )
        # bottom face
        self.assertTrue(
            SelectionGroup((box, SelectionBox((0, -5, 0), (5, 0, 5)))).is_contiguous
        )
        # edge
        self.assertTrue(
            SelectionGroup((box, SelectionBox((0, 5, 5), (5, 10, 10)))).is_contiguous
        )
        # edge partial
        self.assertTrue(
            SelectionGroup((box, SelectionBox((1, 5, 5), (4, 10, 10)))).is_contiguous
        )

        # disconnected top corner
        self.assertFalse(
            SelectionGroup((box, SelectionBox((6, 6, 6), (10, 10, 10)))).is_contiguous
        )
        # intersecting top corner
        self.assertFalse(
            SelectionGroup((box, SelectionBox((4, 4, 4), (10, 10, 10)))).is_contiguous
        )
        # intersecting top face
        self.assertFalse(
            SelectionGroup((box, SelectionBox((0, 4, 0), (5, 10, 5)))).is_contiguous
        )
        # intersecting bottom face
        self.assertFalse(
            SelectionGroup((box, SelectionBox((0, -4, 0), (5, 1, 5)))).is_contiguous
        )
        # intersecting on only two faces
        self.assertFalse(
            SelectionGroup((box, SelectionBox((0, 5, 6), (5, 10, 10)))).is_contiguous
        )

    def test_is_rectangular(self):
        box_1 = SelectionBox((0, 0, 0), (5, 5, 5))
        box_2 = SelectionBox((0, 5, 0), (5, 10, 5))
        box_3 = SelectionBox((0, 0, 5), (5, 5, 10))
        box_4 = SelectionBox((0, 5, 5), (5, 10, 10))

        self.assertTrue(SelectionGroup(box_1).is_rectangular)
        self.assertTrue(SelectionGroup((box_1, box_2)).is_rectangular)
        self.assertFalse(SelectionGroup((box_1, box_2, box_3)).is_rectangular)
        self.assertTrue(SelectionGroup((box_1, box_2, box_3, box_4)).is_rectangular)
        self.assertTrue(
            SelectionGroup((box_1, box_2, box_3, box_4, box_2)).is_rectangular
        )

    def test_single_block_box(self):
        box_1 = SelectionBox((0, 0, 0), (1, 1, 2))

        self.assertEqual((1, 1, 2), box_1.shape)
        self.assertEqual(2, len([x for x in box_1]))

        self.assertIn((0, 0, 0), box_1)
        self.assertNotIn((1, 1, 2), box_1)

    def test_sorted_iterator(self):
        box_1 = SelectionBox((0, 0, 0), (4, 4, 4))
        box_2 = SelectionBox((7, 7, 7), (10, 10, 10))
        box_3 = SelectionBox((15, 15, 15), (20, 20, 20))

        selection_1 = SelectionGroup(
            (
                box_1,
                box_2,
                box_3,
            )
        )
        selection_2 = SelectionGroup(
            (
                box_1,
                box_3,
                box_2,
            )
        )

        self.assertEqual(selection_1, selection_2)

    def test_subtract(self):
        box_1 = SelectionGroup(
            SelectionBox(
                (0, 0, 0),
                (32, 32, 32),
            )
        )
        box_2 = SelectionGroup(
            SelectionBox(
                (0, 0, 0),
                (16, 16, 16),
            )
        )
        box_3 = box_1.subtract(box_2)
        box_4 = SelectionGroup(
            (
                SelectionBox((0, 16, 0), (32, 32, 32)),
                SelectionBox((0, 0, 16), (32, 16, 32)),
                SelectionBox((16, 0, 0), (32, 16, 16)),
            )
        )
        self.assertEqual(box_3, box_4)


if __name__ == "__main__":
    unittest.main()

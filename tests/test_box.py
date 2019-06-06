from test_utils import modify_py_path

modify_py_path()

import unittest
from api import selection


class BoxTestCase(unittest.TestCase):
    def test_intersects(self):
        box_1 = selection.SubBox((0, 0, 0), (5, 5, 5))
        box_2 = selection.SubBox((5, 5, 5), (10, 10, 10))

        self.assertTrue(box_1.intersects(box_2))
        self.assertTrue(box_2.intersects(box_1))

        box_3 = selection.SubBox((6, 6, 6), (10, 10, 10))

        self.assertFalse(box_1.intersects(box_3))
        self.assertFalse(box_3.intersects(box_1))

    def test_is_contiguous(self):
        sub_box_1 = selection.SubBox((0, 0, 0), (5, 5, 5))
        box_1 = selection.SelectionBox((sub_box_1,))

        self.assertTrue(box_1.is_contiguous())

        sub_box_2 = selection.SubBox((6, 6, 6), (10, 10, 10))
        box_1.add_box(sub_box_2)

        self.assertTrue(box_1.is_contiguous())

        sub_box_3 = selection.SubBox((7, 7, 7), (10, 10, 10))
        box_2 = selection.SelectionBox((sub_box_1, sub_box_3))
        self.assertFalse(box_2.is_contiguous())

    def test_is_rectangular(self):
        sub_box_1 = selection.SubBox((0, 0, 0), (5, 5, 5))
        box_1 = selection.SelectionBox((sub_box_1,))

        self.assertTrue(box_1.is_rectangular())

        sub_box_2 = selection.SubBox((0, 5, 0), (5, 10, 5))
        box_1.add_box(sub_box_2)

        self.assertTrue(box_1.is_rectangular())

    def test_add_box(self):  # Quick crude test, needs more cases
        sub_box_1 = selection.SubBox((0, 0, 0), (5, 5, 5))
        box_1 = selection.SelectionBox((sub_box_1,))

        self.assertEqual(1, len(box_1))
        box_1.add_box(selection.SubBox((0, 5, 0), (5, 10, 5)))
        self.assertEqual(1, len(box_1))
        box_1.add_box(selection.SubBox((0, 10, 0), (5, 15, 5)))
        self.assertEqual(1, len(box_1))

        box_2 = selection.SelectionBox((sub_box_1,))
        self.assertEqual(1, len(box_2))
        box_2.add_box(selection.SubBox((0, 6, 0), (5, 10, 5)))
        self.assertEqual(2, len(box_2))

        box_3 = selection.SelectionBox((sub_box_1,))
        self.assertEqual(1, len(box_3))
        box_3.add_box(selection.SubBox((0, 10, 0), (5, 15, 5)))
        self.assertEqual(2, len(box_3))
        box_3.add_box(selection.SubBox((0, 5, 0), (5, 10, 5)))
        self.assertEqual(1, len(box_3))

    def test_single_block_box(self):
        sub_box_1 = selection.SubBox((0, 0, 0), (0, 0, 1))
        box_1 = selection.SelectionBox((sub_box_1,))

        self.assertEqual((0, 0, 1), sub_box_1.shape)
        self.assertEqual(2, len([x for x in sub_box_1]))

        self.assertIn((0, 0, 0), sub_box_1)
        self.assertIn((0, 0, 1), sub_box_1)

        self.assertNotIn((0, 0, 2), sub_box_1)

    def test_sorted_iterator(self):
        sub_box_1 = selection.SubBox((0, 0, 0), (4, 4, 4))
        box_1 = selection.SelectionBox((sub_box_1,))
        box_2 = selection.SelectionBox((sub_box_1,))

        sub_box_2 = selection.SubBox((7, 7, 7), (10, 10, 10))
        box_1.add_box(sub_box_2)

        sub_box_3 = selection.SubBox((15, 15, 15), (20, 20, 20))
        box_2.add_box(sub_box_3)

        box_1.add_box(sub_box_3)
        box_2.add_box(sub_box_2)

        for sb1, sb2 in zip(box_1.subboxes(), box_2.subboxes()):
            self.assertEqual(sb1.shape, sb2.shape)


if __name__ == "__main__":
    unittest.main()

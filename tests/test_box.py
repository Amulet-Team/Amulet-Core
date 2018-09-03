import unittest
from api import box


class BoxTestCase(unittest.TestCase):

    def test_intersects(self):
        box_1 = box.SubBox((0, 0, 0), (5, 5, 5))
        box_2 = box.SubBox((5, 5, 5), (10, 10, 10))

        self.assertTrue(box_1.intersects(box_2))
        self.assertTrue(box_2.intersects(box_1))

        box_3 = box.SubBox((6, 6, 6), (10, 10, 10))

        self.assertFalse(box_1.intersects(box_3))
        self.assertFalse(box_3.intersects(box_1))

    def test_is_contiguous(self):
        sub_box_1 = box.SubBox((0, 0, 0), (5, 5, 5))
        box_1 = box.SelectionBox((sub_box_1,))

        self.assertTrue(box_1.is_contiguous())

        sub_box_2 = box.SubBox((6, 6, 6), (10, 10, 10))
        box_1.add_box(sub_box_2)

        self.assertTrue(box_1.is_contiguous())

        sub_box_3 = box.SubBox((7, 7, 7), (10, 10, 10))
        box_2 = box.SelectionBox((sub_box_1, sub_box_3))
        self.assertFalse(box_2.is_contiguous())

    def test_is_rectangular(self):
        sub_box_1 = box.SubBox((0, 0, 0), (5, 5, 5))
        box_1 = box.SelectionBox((sub_box_1,))

        self.assertTrue(box_1.is_rectangular())

        sub_box_2 = box.SubBox((0, 5, 0), (5, 10, 5))
        box_1.add_box(sub_box_2)

        self.assertTrue(box_1.is_rectangular())

    def test_add_box(self): # Quick crude test, needs more cases
        sub_box_1 = box.SubBox((0, 0, 0), (5, 5, 5))
        box_1 = box.SelectionBox((sub_box_1,))

        self.assertEqual(len(box_1), 1)
        box_1.add_box(box.SubBox((0, 5, 0), (5, 10, 5)))
        self.assertEqual(len(box_1), 1)
        box_1.add_box(box.SubBox((0, 10, 0), (5, 15, 5)))
        self.assertEqual(len(box_1), 1)


        box_2 = box.SelectionBox((sub_box_1,))
        self.assertEqual(len(box_2), 1)
        box_2.add_box(box.SubBox((0, 6, 0), (5, 10, 5)))
        self.assertEqual(len(box_2), 2)

        box_3 = box.SelectionBox((sub_box_1,))
        self.assertEqual(len(box_3), 1)
        box_3.add_box(box.SubBox((0, 10, 0), (5, 15, 5)))
        self.assertEqual(len(box_3), 2)
        box_3.add_box(box.SubBox((0, 5, 0), (5, 10, 5)))
        self.assertEqual(len(box_3), 1)

    def test_single_block_box(self):
        sub_box_1 = box.SubBox((0,0,0),(0,0,1))
        box_1 = box.SelectionBox((sub_box_1,))

        self.assertEqual((0,0,1), sub_box_1.shape)
        self.assertEqual(2, len([x for x in sub_box_1]))

        self.assertTrue((0,0,0) in sub_box_1)
        self.assertTrue((0,0,1) in sub_box_1)

        self.assertFalse((0,0,2) in sub_box_1)

if __name__ == '__main__':
    unittest.main()

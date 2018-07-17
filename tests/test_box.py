import unittest
from editor import box


class BoxTestCase(unittest.TestCase):

    def test_is_contiguous(self):
        sub_box_1 = box.SubBox((0,0,0), (5,5,5))
        box_1 = box.SelectionBox((sub_box_1,))

        self.assertTrue(box_1.is_contiguous())

        sub_box_2 = box.SubBox((6,6,6), (10,10,10))
        box_1.add_box(sub_box_2)

        self.assertTrue(box_1.is_contiguous())

        sub_box_3 = box.SubBox((7,7,7), (10,10,10))
        box_2 = box.SelectionBox((sub_box_1, sub_box_3))
        self.assertFalse(box_2.is_contiguous())


if __name__ == '__main__':
    unittest.main()

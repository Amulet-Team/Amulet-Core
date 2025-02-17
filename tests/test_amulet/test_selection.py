import unittest
import weakref
import gc

from amulet.selection import SelectionGroup, SelectionBox


class SelectionBoxTestCase(unittest.TestCase):
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

        self.assertTrue(box.intersects(SelectionGroup(SelectionBox(0, 0, 0, 1, 1, 1))))
        self.assertTrue(box.intersects(SelectionGroup(SelectionBox(0, 0, 0, 2, 2, 2))))
        self.assertFalse(box.intersects(SelectionGroup(SelectionBox(1, 1, 1, 1, 1, 1))))

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


class SelectionGroupTestCase(unittest.TestCase):
    def test_construct(self) -> None:
        self.assertEqual(0, len(SelectionGroup()))
        self.assertEqual(1, len(SelectionGroup(SelectionBox(0, 1, 2, 3, 4, 5))))
        self.assertEqual(
            2,
            len(
                SelectionGroup(
                    [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)]
                )
            ),
        )
        self.assertEqual(
            2,
            len(
                SelectionGroup(
                    (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
                )
            ),
        )
        self.assertEqual(
            2,
            len(
                SelectionGroup(
                    {SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)}
                )
            ),
        )

    def test_attrs(self) -> None:
        boxes = {SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)}
        group = SelectionGroup(boxes)
        it = group.selection_boxes
        group_ref = weakref.ref(group)
        del group
        gc.collect()
        self.assertIsNotNone(group_ref())
        self.assertEqual(boxes, set(it))

    def test_equals(self) -> None:
        self.assertEqual(
            SelectionGroup(SelectionBox(0, 1, 2, 3, 4, 5)),
            SelectionGroup([SelectionBox(0, 1, 2, 3, 4, 5)]),
        )

        boxes = {
            SelectionBox(0, 1, 2, 3, 4, 5),
            SelectionBox(0, 1, 2, 3, 4, 5),
            SelectionBox(1, 2, 3, 4, 5, 6),
        }
        self.assertEqual(2, len(boxes))
        group = SelectionGroup(boxes)
        self.assertEqual(2, len(group))
        self.assertEqual(boxes, set(group))

        self.assertEqual(
            SelectionGroup(
                (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
            ),
            SelectionGroup(
                {SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)}
            ),
        )
        self.assertEqual(
            SelectionGroup(
                (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
            ),
            SelectionGroup(
                [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)]
            ),
        )
        self.assertEqual(
            SelectionGroup(
                (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
            ),
            SelectionGroup(
                (SelectionBox(1, 2, 3, 4, 5, 6), SelectionBox(0, 1, 2, 3, 4, 5))
            ),
        )
        self.assertNotEqual(
            SelectionGroup(),
            SelectionGroup(
                (SelectionBox(1, 2, 3, 4, 5, 6), SelectionBox(0, 1, 2, 3, 4, 5))
            ),
        )
        self.assertNotEqual(
            SelectionGroup(SelectionBox(1, 2, 3, 4, 5, 6)),
            SelectionGroup(
                (SelectionBox(1, 2, 3, 4, 5, 6), SelectionBox(0, 1, 2, 3, 4, 5))
            ),
        )
        self.assertNotEqual(
            SelectionGroup((SelectionBox(0, 1, 2, 3, 4, 5),)),
            SelectionGroup(
                (SelectionBox(1, 2, 3, 4, 5, 6), SelectionBox(0, 1, 2, 3, 4, 5))
            ),
        )
        for box in [
            SelectionBox(1, 1, 2, 3, 4, 5),
            SelectionBox(0, 2, 2, 3, 4, 5),
            SelectionBox(0, 1, 3, 3, 4, 5),
            SelectionBox(0, 1, 2, 4, 4, 5),
            SelectionBox(0, 1, 2, 3, 5, 5),
            SelectionBox(0, 1, 2, 3, 4, 6),
        ]:
            self.assertNotEqual(
                SelectionGroup(
                    (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
                ),
                SelectionGroup((box, SelectionBox(1, 2, 3, 4, 5, 6))),
            )

    def test_bounds(self) -> None:
        group = SelectionGroup(
            [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)]
        )
        self.assertEqual(0, group.min_x)
        self.assertEqual(1, group.min_y)
        self.assertEqual(2, group.min_z)
        self.assertEqual(5, group.max_x)
        self.assertEqual(7, group.max_y)
        self.assertEqual(9, group.max_z)
        self.assertEqual((0, 1, 2), group.min)
        self.assertEqual((5, 7, 9), group.max)
        self.assertEqual(((0, 1, 2), (5, 7, 9)), group.bounds)
        self.assertEqual(SelectionBox(0, 1, 2, 5, 6, 7), group.bounding_box)

    def test_contains(self) -> None:
        group = SelectionGroup(
            [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)]
        )
        self.assertTrue(group.contains_block(0, 1, 2))
        self.assertTrue(group.contains_block(1, 2, 3))
        self.assertFalse(group.contains_block(0, 0, 0))
        self.assertTrue(group.contains_point(0, 1, 2))
        self.assertTrue(group.contains_point(0.0, 1.0, 2.0))
        self.assertTrue(group.contains_point(1, 2, 3))
        self.assertTrue(group.contains_point(1.0, 2.0, 3.0))
        self.assertFalse(group.contains_point(0, 0, 0))
        self.assertFalse(group.contains_point(0.0, 0.0, 0.0))

    def test_intersects(self) -> None:
        group = SelectionGroup(SelectionBox(-1, -1, -1, 2, 2, 2))

        self.assertTrue(group.intersects(SelectionBox(0, 0, 0, 1, 1, 1)))
        self.assertTrue(group.intersects(SelectionBox(0, 0, 0, 2, 2, 2)))
        self.assertFalse(group.intersects(SelectionBox(1, 1, 1, 1, 1, 1)))

        self.assertTrue(
            group.intersects(SelectionGroup(SelectionBox(0, 0, 0, 1, 1, 1)))
        )
        self.assertTrue(
            group.intersects(SelectionGroup(SelectionBox(0, 0, 0, 2, 2, 2)))
        )
        self.assertFalse(
            group.intersects(SelectionGroup(SelectionBox(1, 1, 1, 1, 1, 1)))
        )

    def test_translate(self) -> None:
        group = SelectionGroup(
            [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)]
        )
        self.assertEqual(
            SelectionGroup(
                [SelectionBox(1, 2, 3, 3, 4, 5), SelectionBox(2, 3, 4, 4, 5, 6)]
            ),
            group.translate(1, 1, 1),
        )
        self.assertEqual(
            SelectionGroup(
                [SelectionBox(-1, 0, 1, 3, 4, 5), SelectionBox(0, 1, 2, 4, 5, 6)]
            ),
            group.translate(-1, -1, -1),
        )

    def test_bool(self) -> None:
        self.assertFalse(SelectionGroup())
        self.assertFalse(SelectionGroup([]))
        self.assertTrue(SelectionGroup(SelectionBox(0, 1, 2, 3, 4, 5)))
        self.assertTrue(SelectionGroup([SelectionBox(0, 1, 2, 3, 4, 5)]))

    # def test_subtract(self) -> None:
    #     box_1 = SelectionGroup(
    #         SelectionBox(
    #             (0, 0, 0),
    #             (32, 32, 32),
    #         )
    #     )
    #     box_2 = SelectionGroup(
    #         SelectionBox(
    #             (0, 0, 0),
    #             (16, 16, 16),
    #         )
    #     )
    #     box_3 = box_1.subtract(box_2)
    #     box_4 = SelectionGroup(
    #         (
    #             SelectionBox((0, 16, 0), (32, 32, 32)),
    #             SelectionBox((0, 0, 16), (32, 16, 32)),
    #             SelectionBox((16, 0, 0), (32, 16, 16)),
    #         )
    #     )
    #     self.assertEqual(box_3, box_4)


if __name__ == "__main__":
    unittest.main()

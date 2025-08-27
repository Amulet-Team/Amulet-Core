import unittest
import weakref
import gc

from amulet.core.selection import SelectionBoxGroup, SelectionBox


class SelectionBoxGroupTestCase(unittest.TestCase):
    def test_cpp(self) -> None:
        from test_amulet_core.test_selection.test_selection_box_group_ import get_tests

        for test in get_tests():
            with self.subTest(test=test.__name__):
                test()

    def test_construct(self) -> None:
        self.assertEqual(0, len(SelectionBoxGroup()))
        self.assertEqual(1, len(SelectionBoxGroup([SelectionBox(0, 1, 2, 3, 4, 5)])))
        self.assertEqual(
            2,
            len(
                SelectionBoxGroup(
                    [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)]
                )
            ),
        )
        self.assertEqual(
            2,
            len(
                SelectionBoxGroup(
                    (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
                )
            ),
        )
        self.assertEqual(
            2,
            len(
                SelectionBoxGroup(
                    {SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)}
                )
            ),
        )

    def test_attrs(self) -> None:
        boxes = {SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)}
        group = SelectionBoxGroup(boxes)
        it = group.boxes
        group_ref = weakref.ref(group)
        del group
        gc.collect()
        self.assertIsNotNone(group_ref())
        self.assertEqual(boxes, set(it))

    def test_equals(self) -> None:
        boxes = {
            SelectionBox(0, 1, 2, 3, 4, 5),
            SelectionBox(0, 1, 2, 3, 4, 5),
            SelectionBox(1, 2, 3, 4, 5, 6),
        }
        self.assertEqual(2, len(boxes))
        group = SelectionBoxGroup(boxes)
        self.assertEqual(2, len(group))
        self.assertEqual(boxes, set(group))

        self.assertEqual(
            SelectionBoxGroup(
                (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
            ),
            SelectionBoxGroup(
                {SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)}
            ),
        )
        self.assertEqual(
            SelectionBoxGroup(
                (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
            ),
            SelectionBoxGroup(
                [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)]
            ),
        )
        self.assertEqual(
            SelectionBoxGroup(
                (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
            ),
            SelectionBoxGroup(
                (SelectionBox(1, 2, 3, 4, 5, 6), SelectionBox(0, 1, 2, 3, 4, 5))
            ),
        )
        self.assertNotEqual(
            SelectionBoxGroup(),
            SelectionBoxGroup(
                (SelectionBox(1, 2, 3, 4, 5, 6), SelectionBox(0, 1, 2, 3, 4, 5))
            ),
        )
        self.assertNotEqual(
            SelectionBoxGroup([SelectionBox(1, 2, 3, 4, 5, 6)]),
            SelectionBoxGroup(
                (SelectionBox(1, 2, 3, 4, 5, 6), SelectionBox(0, 1, 2, 3, 4, 5))
            ),
        )
        self.assertNotEqual(
            SelectionBoxGroup((SelectionBox(0, 1, 2, 3, 4, 5),)),
            SelectionBoxGroup(
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
                SelectionBoxGroup(
                    (SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6))
                ),
                SelectionBoxGroup((box, SelectionBox(1, 2, 3, 4, 5, 6))),
            )

    def test_bounds(self) -> None:
        group = SelectionBoxGroup(
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
        group = SelectionBoxGroup(
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
        group = SelectionBoxGroup([SelectionBox(-1, -1, -1, 2, 2, 2)])

        self.assertTrue(group.intersects(SelectionBox(0, 0, 0, 1, 1, 1)))
        self.assertTrue(group.intersects(SelectionBox(0, 0, 0, 2, 2, 2)))
        self.assertFalse(group.intersects(SelectionBox(1, 1, 1, 1, 1, 1)))

        self.assertTrue(
            group.intersects(SelectionBoxGroup([SelectionBox(0, 0, 0, 1, 1, 1)]))
        )
        self.assertTrue(
            group.intersects(SelectionBoxGroup([SelectionBox(0, 0, 0, 2, 2, 2)]))
        )
        self.assertFalse(
            group.intersects(SelectionBoxGroup([SelectionBox(1, 1, 1, 1, 1, 1)]))
        )

    def test_translate(self) -> None:
        group = SelectionBoxGroup(
            [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(1, 2, 3, 4, 5, 6)]
        )
        self.assertEqual(
            SelectionBoxGroup(
                [SelectionBox(1, 2, 3, 3, 4, 5), SelectionBox(2, 3, 4, 4, 5, 6)]
            ),
            group.translate(1, 1, 1),
        )
        self.assertEqual(
            SelectionBoxGroup(
                [SelectionBox(-1, 0, 1, 3, 4, 5), SelectionBox(0, 1, 2, 4, 5, 6)]
            ),
            group.translate(-1, -1, -1),
        )

    def test_bool(self) -> None:
        self.assertFalse(SelectionBoxGroup())
        self.assertFalse(SelectionBoxGroup([]))
        self.assertTrue(SelectionBoxGroup([SelectionBox(0, 1, 2, 3, 4, 5)]))

    # def test_subtract(self) -> None:
    #     box_1 = SelectionBoxGroup(
    #         SelectionBox(
    #             (0, 0, 0),
    #             (32, 32, 32),
    #         )
    #     )
    #     box_2 = SelectionBoxGroup(
    #         SelectionBox(
    #             (0, 0, 0),
    #             (16, 16, 16),
    #         )
    #     )
    #     box_3 = box_1.subtract(box_2)
    #     box_4 = SelectionBoxGroup(
    #         (
    #             SelectionBox((0, 16, 0), (32, 32, 32)),
    #             SelectionBox((0, 0, 16), (32, 16, 32)),
    #             SelectionBox((16, 0, 0), (32, 16, 16)),
    #         )
    #     )
    #     self.assertEqual(box_3, box_4)


if __name__ == "__main__":
    unittest.main()

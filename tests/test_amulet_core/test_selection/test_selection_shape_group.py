import copy
import unittest

from amulet.utils.matrix import Matrix4x4

from amulet.core.selection import (
    SelectionShapeGroup,
    SelectionCuboid,
    SelectionEllipsoid,
    SelectionBoxGroup,
    SelectionBox,
)
from test_amulet_core.test_selection.test_selection_shape_group_ import get_cuboid_ref


class SelectionShapeGroupTestCase(unittest.TestCase):
    def test_cpp(self) -> None:
        from test_amulet_core.test_selection.test_selection_shape_group_ import (
            get_tests,
        )

        for test in get_tests():
            with self.subTest(test=test.__name__):
                test()

    def test_constructor_iter(self) -> None:
        group_1 = SelectionShapeGroup()
        self.assertEqual(0, len(group_1))

        group_2 = SelectionShapeGroup(
            [
                SelectionCuboid(0, 1, 2, 3, 4, 5),
                SelectionCuboid(6, 7, 8, 9, 10, 11),
                SelectionCuboid(12, 13, 14, 15, 16, 17),
            ]
        )
        self.assertEqual(3, len(group_2))

        # Test mutation
        cuboid = SelectionCuboid(0, 1, 2, 3, 4, 5)
        cuboid_ref = get_cuboid_ref(cuboid)
        group_3 = SelectionShapeGroup([cuboid, cuboid_ref])
        group_3[0].matrix.set_element(0, 0, 10)
        group_3[1].matrix.set_element(0, 0, 20)
        self.assertAlmostEqual(10.0, cuboid.matrix.get_element(0, 0))
        self.assertNotAlmostEqual(20.0, cuboid_ref.matrix.get_element(0, 0))

    def test_constructor_box_group(self) -> None:
        box_group = SelectionBoxGroup(
            [SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(6, 7, 8, 9, 10, 11)]
        )
        shape_group = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4, 5), SelectionCuboid(6, 7, 8, 9, 10, 11)]
        )
        self.assertTrue(shape_group.almost_equal(SelectionShapeGroup(box_group)))

    def test_cuboid_ref(self) -> None:
        cuboid = SelectionCuboid(1, 2, 3, 4, 5, 6)
        cuboid_ref = get_cuboid_ref(cuboid)
        self.assertAlmostEqual(
            cuboid.matrix.get_element(0, 0), cuboid_ref.matrix.get_element(0, 0)
        )
        cuboid.matrix.set_element(0, 0, 10)
        self.assertNotAlmostEqual(
            cuboid.matrix.get_element(0, 0), cuboid_ref.matrix.get_element(0, 0)
        )
        cuboid_ref = get_cuboid_ref(cuboid)
        self.assertAlmostEqual(
            cuboid.matrix.get_element(0, 0), cuboid_ref.matrix.get_element(0, 0)
        )

    def test_constructor_ref(self) -> None:
        # It is possible for a python object to not directly own the pointer
        # Make sure it can be constructed from this type
        group_1 = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4, 5), SelectionCuboid(1, 2, 3, 4, 5, 6)]
        )
        group_2 = SelectionShapeGroup(
            [
                SelectionCuboid(0, 1, 2, 3, 4, 5),
                get_cuboid_ref(SelectionCuboid(1, 2, 3, 4, 5, 6)),
            ]
        )
        self.assertTrue(group_1.almost_equal(group_2))

    def test_constructor_errors(self) -> None:
        with self.assertRaises(RuntimeError):
            SelectionShapeGroup(["test"])  # type: ignore
        with self.assertRaises(RuntimeError):
            SelectionShapeGroup([5])  # type: ignore

    def test_copy(self) -> None:
        cuboid = SelectionCuboid(0, 1, 2, 3, 4, 5)

        group_1 = SelectionShapeGroup([cuboid])
        group_2 = copy.copy(group_1)
        cuboid.matrix.set_element(0, 0, 20)
        self.assertAlmostEqual(20.0, group_1[0].matrix.get_element(0, 0))
        self.assertAlmostEqual(20.0, group_2[0].matrix.get_element(0, 0))

    def test_deepcopy(self) -> None:
        cuboid = SelectionCuboid(0, 1, 2, 3, 4, 5)

        group_1 = SelectionShapeGroup([cuboid])
        group_2 = copy.deepcopy(group_1)
        cuboid.matrix.set_element(0, 0, 20)
        self.assertAlmostEqual(20.0, group_1[0].matrix.get_element(0, 0))
        self.assertNotAlmostEqual(20.0, group_2[0].matrix.get_element(0, 0))

    def test_serialisation(self) -> None:
        group = SelectionShapeGroup(
            [
                SelectionCuboid(0, 1, 2, 3, 4, 5),
                SelectionEllipsoid(0, 1, 2, 3),
                SelectionCuboid(
                    Matrix4x4.transformation_matrix(1, 2, 3, 4, 5, 6, 7, 8, 9)
                ),
                SelectionEllipsoid(
                    Matrix4x4.transformation_matrix(1, 2, 3, 4, 5, 6, 7, 8, 9)
                ),
            ]
        )
        serialised = group.serialise()
        self.assertIsInstance(serialised, str)
        self.assertTrue(group.almost_equal(SelectionShapeGroup.deserialise(serialised)))

        with self.assertRaises(RuntimeError):
            SelectionShapeGroup.deserialise("")

    def test_voxelise(self) -> None:
        shape_group = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4, 5), SelectionCuboid(6, 7, 8, 9, 10, 11)]
        )
        box_group = shape_group.voxelise()
        self.assertEqual(2, len(box_group))
        self.assertEqual(
            {SelectionBox(0, 1, 2, 3, 4, 5), SelectionBox(6, 7, 8, 9, 10, 11)},
            set(box_group),
        )

    def test_almost_equal(self) -> None:
        group_1 = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4, 5), SelectionCuboid(6, 7, 8, 9, 10, 11)]
        )
        group_2 = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4, 5), SelectionCuboid(6, 7, 8, 9, 10, 11)]
        )
        group_3 = SelectionShapeGroup(
            [SelectionCuboid(0, 1.1, 2, 3, 4, 5), SelectionCuboid(6, 7, 8, 9, 10, 11)]
        )
        group_4 = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4.1, 5), SelectionCuboid(6, 7, 8, 9, 10, 11)]
        )
        group_5 = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4, 5), SelectionCuboid(6, 7.1, 8, 9, 10, 11)]
        )
        group_6 = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4, 5), SelectionCuboid(6, 7, 8, 9, 10.1, 11)]
        )
        group_7 = SelectionShapeGroup([SelectionCuboid(0, 1, 2, 3, 4, 5)])
        group_8 = SelectionShapeGroup(
            [
                SelectionCuboid(0, 1, 2, 3, 4, 5),
                SelectionCuboid(6, 7, 8, 9, 10, 11),
                SelectionCuboid(12, 13, 14, 15, 16, 17),
            ]
        )
        self.assertTrue(group_1.almost_equal(SelectionShapeGroup(group_2)))
        self.assertFalse(group_1.almost_equal(SelectionShapeGroup(group_3)))
        self.assertFalse(group_1.almost_equal(SelectionShapeGroup(group_4)))
        self.assertFalse(group_1.almost_equal(SelectionShapeGroup(group_5)))
        self.assertFalse(group_1.almost_equal(SelectionShapeGroup(group_6)))
        self.assertFalse(group_1.almost_equal(SelectionShapeGroup(group_7)))
        self.assertFalse(group_1.almost_equal(SelectionShapeGroup(group_8)))

    def test_bool(self) -> None:
        self.assertFalse(SelectionShapeGroup())
        self.assertTrue(SelectionShapeGroup([SelectionCuboid(0, 1, 2, 3, 4, 5)]))

    def test_len(self) -> None:
        self.assertEqual(0, len(SelectionShapeGroup()))
        self.assertEqual(
            1, len(SelectionShapeGroup([SelectionCuboid(0, 1, 2, 3, 4, 5)]))
        )
        self.assertEqual(
            2,
            len(
                SelectionShapeGroup(
                    [
                        SelectionCuboid(0, 1, 2, 3, 4, 5),
                        SelectionCuboid(6, 7, 8, 9, 10, 11),
                    ]
                )
            ),
        )

    def test_getitem(self) -> None:
        group_1 = SelectionShapeGroup()
        with self.assertRaises(IndexError):
            _ = group_1[0]

        cuboid_1 = SelectionCuboid(0, 1, 2, 3, 4, 5)
        cuboid_2 = SelectionCuboid(6, 7, 8, 9, 10, 11)
        cuboid_3 = SelectionCuboid(12, 13, 14, 15, 16, 17)
        group_2 = SelectionShapeGroup([cuboid_1, cuboid_2, cuboid_3])

        with self.assertRaises(IndexError):
            _ = group_2[-4]
        self.assertIs(cuboid_1, group_2[-3])
        self.assertIs(cuboid_2, group_2[-2])
        self.assertIs(cuboid_3, group_2[-1])
        self.assertIs(cuboid_1, group_2[0])
        self.assertIs(cuboid_2, group_2[1])
        self.assertIs(cuboid_3, group_2[2])
        with self.assertRaises(IndexError):
            _ = group_2[3]

    def test_setitem(self) -> None:
        cuboid_1 = SelectionCuboid(0, 1, 2, 3, 4, 5)
        cuboid_2 = SelectionCuboid(6, 7, 8, 9, 10, 11)
        cuboid_3 = SelectionCuboid(12, 13, 14, 15, 16, 17)
        group = SelectionShapeGroup([cuboid_1, cuboid_2, cuboid_3])

        with self.assertRaises(IndexError):
            group[-4] = SelectionCuboid(0, 1, 2, 3, 4, 5)
        with self.assertRaises(IndexError):
            group[3] = SelectionCuboid(0, 1, 2, 3, 4, 5)

        group[-3] = cuboid_2
        group[-2] = cuboid_3
        group[-1] = cuboid_1
        self.assertIs(cuboid_2, group[0])
        self.assertIs(cuboid_3, group[1])
        self.assertIs(cuboid_1, group[2])

        group[0] = cuboid_3
        group[1] = cuboid_1
        group[2] = cuboid_2
        self.assertIs(cuboid_3, group[0])
        self.assertIs(cuboid_1, group[1])
        self.assertIs(cuboid_2, group[2])

    def test_delitem(self) -> None:
        cuboid_1 = SelectionCuboid(0, 1, 2, 3, 4, 5)
        cuboid_2 = SelectionCuboid(6, 7, 8, 9, 10, 11)
        cuboid_3 = SelectionCuboid(12, 13, 14, 15, 16, 17)
        group = SelectionShapeGroup([cuboid_1, cuboid_2, cuboid_3])

        with self.assertRaises(IndexError):
            del group[-4]
        with self.assertRaises(IndexError):
            del group[3]
        self.assertIs(cuboid_1, group[0])
        self.assertIs(cuboid_2, group[1])
        self.assertIs(cuboid_3, group[2])

        group_copy = copy.copy(group)
        del group_copy[0]
        self.assertEqual(2, len(group_copy))
        self.assertIs(cuboid_2, group_copy[0])
        self.assertIs(cuboid_3, group_copy[1])

        group_copy = copy.copy(group)
        del group_copy[1]
        self.assertEqual(2, len(group_copy))
        self.assertIs(cuboid_1, group_copy[0])
        self.assertIs(cuboid_3, group_copy[1])

        group_copy = copy.copy(group)
        del group_copy[-2]
        self.assertEqual(2, len(group_copy))
        self.assertIs(cuboid_1, group_copy[0])
        self.assertIs(cuboid_3, group_copy[1])

    def test_insert(self) -> None:
        cuboid_1 = SelectionCuboid(0, 1, 2, 3, 4, 5)
        cuboid_2 = SelectionCuboid(6, 7, 8, 9, 10, 11)
        cuboid_3 = SelectionCuboid(12, 13, 14, 15, 16, 17)
        cuboid_4 = SelectionCuboid(18, 19, 20, 21, 22, 23)
        cuboid_5 = SelectionCuboid(24, 25, 26, 27, 28, 29)
        cuboid_6 = SelectionCuboid(30, 31, 32, 33, 34, 35)
        group = SelectionShapeGroup()

        group.insert(0, cuboid_1)
        self.assertEqual(1, len(group))
        self.assertIs(cuboid_1, group[0])

        group.clear()
        group.insert(10, cuboid_1)
        self.assertEqual(1, len(group))
        self.assertIs(cuboid_1, group[0])

        group.clear()
        group.insert(-10, cuboid_1)
        self.assertEqual(1, len(group))
        self.assertIs(cuboid_1, group[0])

        group.insert(-10, cuboid_2)
        group.insert(10, cuboid_3)
        group.insert(1, cuboid_4)
        group.insert(-1, cuboid_5)
        group.insert(2, cuboid_6)

        self.assertEqual(6, len(group))
        self.assertIs(cuboid_2, group[0])
        self.assertIs(cuboid_4, group[1])
        self.assertIs(cuboid_6, group[2])
        self.assertIs(cuboid_1, group[3])
        self.assertIs(cuboid_5, group[4])
        self.assertIs(cuboid_3, group[5])

    def test_repr(self) -> None:
        group = SelectionShapeGroup(
            [SelectionCuboid(0, 1, 2, 3, 4, 5), SelectionEllipsoid(6, 7, 8, 9)]
        )
        r = repr(group)
        self.assertIsInstance(r, str)
        import amulet

        self.assertTrue(group.almost_equal(eval(r, {"amulet": amulet})))


if __name__ == "__main__":
    unittest.main()

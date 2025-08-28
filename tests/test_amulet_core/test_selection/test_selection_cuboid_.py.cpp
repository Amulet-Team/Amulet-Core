#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <amulet/test_utils/test_utils.hpp>

#include <amulet/core/selection/box.hpp>
#include <amulet/core/selection/box_group.hpp>
#include <amulet/core/selection/cuboid.hpp>
#include <amulet/core/selection/ellipsoid.hpp>

namespace py = pybind11;

void init_test_selection_cuboid(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_selection_cuboid_");

    m.def(
        "get_tests",
        []() -> py::typing::List<py::typing::Callable<void()>> {
            py::list tests;

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid(Amulet::Matrix4x4::scale_matrix(1, 2, 3).translate(10, 20, 30));
                        auto group = cuboid.voxelise();
                        ASSERT_EQUAL(size_t, 1, group.count());
                        std::set<Amulet::SelectionBox> boxes_expected({ Amulet::SelectionBox(10, 20, 30, 1, 2, 3) });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_constructor_matrix")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid(10, 20, 30, 1, 2, 3);
                        auto group = cuboid.voxelise();
                        ASSERT_EQUAL(size_t, 1, group.count());
                        std::set<Amulet::SelectionBox> boxes_expected({ Amulet::SelectionBox(10, 20, 30, 1, 2, 3) });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_constructor_box")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        Amulet::SelectionCuboid cuboid2(cuboid1);
                        auto group = cuboid2.voxelise();
                        ASSERT_EQUAL(size_t, 1, group.count());
                        std::set<Amulet::SelectionBox> boxes_expected({ Amulet::SelectionBox(10, 20, 30, 1, 2, 3) });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_constructor_copy")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        auto cuboid2 = cuboid1.copy();
                        bool is_same = std::is_same_v<std::unique_ptr<Amulet::SelectionShape>, decltype(cuboid2)>;
                        ASSERT_TRUE(is_same);
                        auto group = cuboid2->voxelise();
                        ASSERT_EQUAL(size_t, 1, group.count());
                        std::set<Amulet::SelectionBox> boxes_expected({ Amulet::SelectionBox(10, 20, 30, 1, 2, 3) });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_copy")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        auto cuboid2 = static_cast<std::unique_ptr<Amulet::SelectionShape>>(cuboid1);
                        bool is_same = std::is_same_v<std::unique_ptr<Amulet::SelectionShape>, decltype(cuboid2)>;
                        ASSERT_TRUE(is_same);
                        auto group = cuboid2->voxelise();
                        ASSERT_EQUAL(size_t, 1, group.count());
                        std::set<Amulet::SelectionBox> boxes_expected({ Amulet::SelectionBox(10, 20, 30, 1, 2, 3) });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_operator_unique_ptr")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid(10, 20, 30, 1, 2, 3);
                        auto boxes = static_cast<std::set<Amulet::SelectionBox>>(cuboid);
                        ASSERT_EQUAL(size_t, 1, boxes.size());
                        std::set<Amulet::SelectionBox> boxes_expected({ Amulet::SelectionBox(10, 20, 30, 1, 2, 3) });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, boxes);
                    },
                    py::name("test_operator_set")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid(10, 20, 30, 1, 2, 3);
                        auto group = static_cast<Amulet::SelectionBoxGroup>(cuboid);
                        bool is_same = std::is_same_v<Amulet::SelectionBoxGroup, decltype(group)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_EQUAL(size_t, 1, group.count());
                        std::set<Amulet::SelectionBox> boxes_expected({ Amulet::SelectionBox(10, 20, 30, 1, 2, 3) });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_operator_box_group")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid(10, 20, 30, 1, 2, 3);
                        auto group = cuboid.voxelise();
                        bool is_same = std::is_same_v<Amulet::SelectionBoxGroup, decltype(group)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_EQUAL(size_t, 1, group.count());
                        std::set<Amulet::SelectionBox> boxes_expected({ Amulet::SelectionBox(10, 20, 30, 1, 2, 3) });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_voxelise")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        auto cuboid2 = cuboid1.translate_cuboid(0.5, 1.5, 2.5);
                        bool is_same = std::is_same_v<Amulet::SelectionCuboid, decltype(cuboid2)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(cuboid2.almost_equal(Amulet::SelectionCuboid(10.5, 21.5, 32.5, 1, 2, 3)));
                    },
                    py::name("test_translate_cuboid")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        auto cuboid2 = cuboid1.transform_cuboid(Amulet::Matrix4x4::translation_matrix(0.5, 1.5, 2.5));
                        bool is_same = std::is_same_v<Amulet::SelectionCuboid, decltype(cuboid2)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(cuboid2.almost_equal(Amulet::SelectionCuboid(10.5, 21.5, 32.5, 1, 2, 3)));
                    },
                    py::name("test_transform_cuboid")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        auto cuboid2 = cuboid1.translate(0.5, 1.5, 2.5);
                        bool is_same = std::is_same_v<std::unique_ptr<Amulet::SelectionShape>, decltype(cuboid2)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(cuboid2->almost_equal(Amulet::SelectionCuboid(10.5, 21.5, 32.5, 1, 2, 3)));
                    },
                    py::name("test_translate")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        auto cuboid2 = cuboid1.transform(Amulet::Matrix4x4::translation_matrix(0.5, 1.5, 2.5));
                        bool is_same = std::is_same_v<std::unique_ptr<Amulet::SelectionShape>, decltype(cuboid2)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(cuboid2->almost_equal(Amulet::SelectionCuboid(10.5, 21.5, 32.5, 1, 2, 3)));
                    },
                    py::name("test_transform")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        ASSERT_TRUE(cuboid1.almost_equal(Amulet::SelectionCuboid(10, 20, 30, 1, 2, 3)));
                        ASSERT_FALSE(cuboid1.almost_equal(Amulet::SelectionCuboid(10.1, 20, 30, 1, 2, 3)));
                        ASSERT_FALSE(cuboid1.almost_equal(Amulet::SelectionCuboid(10, 20.1, 30, 1, 2, 3)));
                        ASSERT_FALSE(cuboid1.almost_equal(Amulet::SelectionCuboid(10, 20, 30.1, 1, 2, 3)));
                        ASSERT_FALSE(cuboid1.almost_equal(Amulet::SelectionCuboid(10, 20, 30, 1.1, 2, 3)));
                        ASSERT_FALSE(cuboid1.almost_equal(Amulet::SelectionCuboid(10, 20, 30, 1, 2.1, 3)));
                        ASSERT_FALSE(cuboid1.almost_equal(Amulet::SelectionCuboid(10, 20, 30, 1, 2, 3.1)));
                    },
                    py::name("test_almost_equal_cuboid")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionCuboid cuboid1(10, 20, 30, 1, 2, 3);
                        ASSERT_TRUE(cuboid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionCuboid(10, 20, 30, 1, 2, 3))));
                        ASSERT_FALSE(cuboid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionCuboid(10.1, 20, 30, 1, 2, 3))));
                        ASSERT_FALSE(cuboid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionCuboid(10, 20.1, 30, 1, 2, 3))));
                        ASSERT_FALSE(cuboid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionCuboid(10, 20, 30.1, 1, 2, 3))));
                        ASSERT_FALSE(cuboid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionCuboid(10, 20, 30, 1.1, 2, 3))));
                        ASSERT_FALSE(cuboid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionCuboid(10, 20, 30, 1, 2.1, 3))));
                        ASSERT_FALSE(cuboid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionCuboid(10, 20, 30, 1, 2, 3.1))));
                        ASSERT_FALSE(cuboid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionEllipsoid(10, 20, 30, 1))));
                    },
                    py::name("test_almost_equal_shape")));

            return tests;
        });
}

#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <amulet/test_utils/test_utils.hpp>

#include <amulet/core/selection/box.hpp>
#include <amulet/core/selection/box_group.hpp>
#include <amulet/core/selection/cuboid.hpp>
#include <amulet/core/selection/ellipsoid.hpp>

namespace py = pybind11;

void init_test_selection_ellipsoid(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_selection_ellipsoid_");

    m.def(
        "get_tests",
        []() -> py::typing::List<py::typing::Callable<void()>> {
            py::list tests;

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid(Amulet::Matrix4x4::scale_matrix(10, 20, 30).translate(10, 20, 30));
                        ASSERT_TRUE(ellipsoid.get_matrix().almost_equal(Amulet::Matrix4x4::scale_matrix(10, 20, 30).translate(10, 20, 30)));
                    },
                    py::name("test_constructor_matrix")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid(1, 2, 3, 4);
                        ASSERT_TRUE(ellipsoid.get_matrix().almost_equal(Amulet::Matrix4x4::scale_matrix(8, 8, 8).translate(1, 2, 3)));
                    },
                    py::name("test_constructor_sphere")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid1(1, 2, 3, 4);
                        Amulet::SelectionEllipsoid ellipsoid2(ellipsoid1);
                        ASSERT_TRUE(ellipsoid2.get_matrix().almost_equal(Amulet::Matrix4x4::scale_matrix(8, 8, 8).translate(1, 2, 3)));
                    },
                    py::name("test_constructor_copy")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid(1, 2, 3, 4);
                        auto shape = ellipsoid.copy();
                        bool is_same = std::is_same_v<std::unique_ptr<Amulet::SelectionShape>, decltype(shape)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(shape->get_matrix().almost_equal(Amulet::Matrix4x4::scale_matrix(8, 8, 8).translate(1, 2, 3)));
                        ASSERT_TRUE(dynamic_cast<Amulet::SelectionEllipsoid*>(shape.get()));
                    },
                    py::name("test_copy")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid(1, 2, 3, 4);
                        auto shape = static_cast<std::unique_ptr<Amulet::SelectionShape>>(ellipsoid);
                        bool is_same = std::is_same_v<std::unique_ptr<Amulet::SelectionShape>, decltype(shape)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(shape->get_matrix().almost_equal(Amulet::Matrix4x4::scale_matrix(8, 8, 8).translate(1, 2, 3)));
                        ASSERT_TRUE(dynamic_cast<Amulet::SelectionEllipsoid*>(shape.get()));
                    },
                    py::name("test_operator_unique_ptr")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid(1, 2, 3, 4);
                        auto boxes = static_cast<std::set<Amulet::SelectionBox>>(ellipsoid);
                        ASSERT_LESS(size_t, 5, boxes.size());
                    },
                    py::name("test_operator_set")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid(1, 2, 3, 4);
                        auto group = static_cast<Amulet::SelectionBoxGroup>(ellipsoid);
                        bool is_same = std::is_same_v<Amulet::SelectionBoxGroup, decltype(group)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_LESS(size_t, 5, group.count());
                    },
                    py::name("test_operator_box_group")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid(1, 2, 3, 4);
                        auto group = ellipsoid.voxelise();
                        bool is_same = std::is_same_v<Amulet::SelectionBoxGroup, decltype(group)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_LESS(size_t, 5, group.count());
                    },
                    py::name("test_voxelise")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid1(1, 2, 3, 4);
                        auto ellipsoid2 = ellipsoid1.translate_ellipsoid(0.5, 1.5, 2.5);
                        bool is_same = std::is_same_v<Amulet::SelectionEllipsoid, decltype(ellipsoid2)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(ellipsoid2.almost_equal(Amulet::SelectionEllipsoid(1.5, 3.5, 5.5, 4)));
                    },
                    py::name("test_translate_ellipsoid")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid1(1, 2, 3, 4);
                        auto ellipsoid2 = ellipsoid1.transform_ellipsoid(Amulet::Matrix4x4::translation_matrix(0.5, 1.5, 2.5));
                        bool is_same = std::is_same_v<Amulet::SelectionEllipsoid, decltype(ellipsoid2)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(ellipsoid2.almost_equal(Amulet::SelectionEllipsoid(1.5, 3.5, 5.5, 4)));
                    },
                    py::name("test_transform_ellipsoid")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid1(1, 2, 3, 4);
                        auto ellipsoid2 = ellipsoid1.translate(0.5, 1.5, 2.5);
                        bool is_same = std::is_same_v<std::unique_ptr<Amulet::SelectionShape>, decltype(ellipsoid2)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(ellipsoid2->almost_equal(Amulet::SelectionEllipsoid(1.5, 3.5, 5.5, 4)));
                    },
                    py::name("test_translate")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid1(1, 2, 3, 4);
                        auto ellipsoid2 = ellipsoid1.transform(Amulet::Matrix4x4::translation_matrix(0.5, 1.5, 2.5));
                        bool is_same = std::is_same_v<std::unique_ptr<Amulet::SelectionShape>, decltype(ellipsoid2)>;
                        ASSERT_TRUE(is_same);
                        ASSERT_TRUE(ellipsoid2->almost_equal(Amulet::SelectionEllipsoid(1.5, 3.5, 5.5, 4)));
                    },
                    py::name("test_transform")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid1(1, 2, 3, 4);
                        ASSERT_TRUE(ellipsoid1.almost_equal(Amulet::SelectionEllipsoid(1, 2, 3, 4)));
                        ASSERT_FALSE(ellipsoid1.almost_equal(Amulet::SelectionEllipsoid(1.1, 2, 3, 4)));
                        ASSERT_FALSE(ellipsoid1.almost_equal(Amulet::SelectionEllipsoid(1, 2.1, 3, 4)));
                        ASSERT_FALSE(ellipsoid1.almost_equal(Amulet::SelectionEllipsoid(1, 2, 3.1, 4)));
                        ASSERT_FALSE(ellipsoid1.almost_equal(Amulet::SelectionEllipsoid(1, 2, 3, 4.1)));
                    },
                    py::name("test_almost_equal_ellipsoid")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionEllipsoid ellipsoid1(1, 2, 3, 4);
                        ASSERT_TRUE(ellipsoid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionEllipsoid(1, 2, 3, 4))));
                        ASSERT_FALSE(ellipsoid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionEllipsoid(1.1, 2, 3, 4))));
                        ASSERT_FALSE(ellipsoid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionEllipsoid(1, 2.1, 3, 4))));
                        ASSERT_FALSE(ellipsoid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionEllipsoid(1, 2, 3.1, 4))));
                        ASSERT_FALSE(ellipsoid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionEllipsoid(1, 2, 3, 4.1))));
                        ASSERT_FALSE(ellipsoid1.almost_equal(static_cast<const Amulet::SelectionShape&>(Amulet::SelectionCuboid(10, 20, 30, 1, 2, 3))));
                    },
                    py::name("test_almost_equal_shape")));

            return tests;
        });
}

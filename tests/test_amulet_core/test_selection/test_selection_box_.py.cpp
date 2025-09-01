#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <numbers>

#include <amulet/test_utils/test_utils.hpp>

#include <amulet/utils/matrix.hpp>

#include <amulet/core/selection/box.hpp>
#include <amulet/core/selection/box_group.hpp>

namespace py = pybind11;

void init_test_selection_box(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_selection_box_");

    m.def(
        "get_tests",
        []() -> py::typing::List<py::typing::Callable<void()>> {
            py::list tests;

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(1, 2, 3, 4, 5, 6);
                        ASSERT_EQUAL(std::int64_t, 1, box1.min_x());
                        ASSERT_EQUAL(std::int64_t, 2, box1.min_y());
                        ASSERT_EQUAL(std::int64_t, 3, box1.min_z());
                        ASSERT_EQUAL(std::int64_t, 5, box1.max_x());
                        ASSERT_EQUAL(std::int64_t, 7, box1.max_y());
                        ASSERT_EQUAL(std::int64_t, 9, box1.max_z());

                        Amulet::SelectionBox box2(-1, -2, -3, 4, 6, 8);
                        ASSERT_EQUAL(std::int64_t, -1, box2.min_x());
                        ASSERT_EQUAL(std::int64_t, -2, box2.min_y());
                        ASSERT_EQUAL(std::int64_t, -3, box2.min_z());
                        ASSERT_EQUAL(std::int64_t, 3, box2.max_x());
                        ASSERT_EQUAL(std::int64_t, 4, box2.max_y());
                        ASSERT_EQUAL(std::int64_t, 5, box2.max_z());
                    },
                    py::name("test_construct_bounds")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1({ 1, 2, 3 }, { 4, 5, 6 });
                        ASSERT_EQUAL(std::int64_t, 1, box1.min_x());
                        ASSERT_EQUAL(std::int64_t, 2, box1.min_y());
                        ASSERT_EQUAL(std::int64_t, 3, box1.min_z());
                        ASSERT_EQUAL(std::int64_t, 4, box1.max_x());
                        ASSERT_EQUAL(std::int64_t, 5, box1.max_y());
                        ASSERT_EQUAL(std::int64_t, 6, box1.max_z());

                        Amulet::SelectionBox box2({ -1, -6, -3 }, { -4, -2, -8 });
                        ASSERT_EQUAL(std::int64_t, -4, box2.min_x());
                        ASSERT_EQUAL(std::int64_t, -6, box2.min_y());
                        ASSERT_EQUAL(std::int64_t, -8, box2.min_z());
                        ASSERT_EQUAL(std::int64_t, -1, box2.max_x());
                        ASSERT_EQUAL(std::int64_t, -2, box2.max_y());
                        ASSERT_EQUAL(std::int64_t, -3, box2.max_z());
                    },
                    py::name("test_construct_points")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(1, 2, 3, 4, 5, 6);

                        Amulet::SelectionBox box2(box1);
                        ASSERT_EQUAL(std::int64_t, 1, box2.min_x());
                        ASSERT_EQUAL(std::int64_t, 2, box2.min_y());
                        ASSERT_EQUAL(std::int64_t, 3, box2.min_z());
                        ASSERT_EQUAL(std::int64_t, 5, box2.max_x());
                        ASSERT_EQUAL(std::int64_t, 7, box2.max_y());
                        ASSERT_EQUAL(std::int64_t, 9, box2.max_z());
                    },
                    py::name("test_construct_copy")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box(1, 2, 3, 4, 5, 6);
                        ASSERT_EQUAL(std::int64_t, 1, box.min_x());
                        ASSERT_EQUAL(std::int64_t, 2, box.min_y());
                        ASSERT_EQUAL(std::int64_t, 3, box.min_z());
                        ASSERT_EQUAL(std::int64_t, 5, box.max_x());
                        ASSERT_EQUAL(std::int64_t, 7, box.max_y());
                        ASSERT_EQUAL(std::int64_t, 9, box.max_z());
                        ASSERT_EQUAL(std::int64_t, 1, box.min()[0]);
                        ASSERT_EQUAL(std::int64_t, 2, box.min()[1]);
                        ASSERT_EQUAL(std::int64_t, 3, box.min()[2]);
                        ASSERT_EQUAL(std::int64_t, 5, box.max()[0]);
                        ASSERT_EQUAL(std::int64_t, 7, box.max()[1]);
                        ASSERT_EQUAL(std::int64_t, 9, box.max()[2]);
                        ASSERT_EQUAL(std::uint64_t, 4, box.size_x());
                        ASSERT_EQUAL(std::uint64_t, 5, box.size_y());
                        ASSERT_EQUAL(std::uint64_t, 6, box.size_z());
                        ASSERT_EQUAL(std::uint64_t, 4, box.shape()[0]);
                        ASSERT_EQUAL(std::uint64_t, 5, box.shape()[1]);
                        ASSERT_EQUAL(std::uint64_t, 6, box.shape()[2]);
                        ASSERT_EQUAL(std::uint64_t, 120, box.volume());
                    },
                    py::name("test_attrs")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(1, 2, 3, 4, 5, 6);
                        ASSERT_TRUE(box1.contains_block(1, 2, 3));
                        ASSERT_TRUE(box1.contains_block(4, 6, 8));

                        ASSERT_FALSE(box1.contains_block(0, 2, 3));
                        ASSERT_FALSE(box1.contains_block(1, 1, 3));
                        ASSERT_FALSE(box1.contains_block(1, 2, 2));
                        ASSERT_FALSE(box1.contains_block(5, 6, 8));
                        ASSERT_FALSE(box1.contains_block(4, 7, 8));
                        ASSERT_FALSE(box1.contains_block(4, 6, 9));

                        Amulet::SelectionBox box2(-10, -11, -12, 1, 2, 3);
                        ASSERT_TRUE(box2.contains_block(-10, -11, -12));
                        ASSERT_TRUE(box2.contains_block(-10, -10, -10));

                        ASSERT_FALSE(box2.contains_block(-11, -11, -12));
                        ASSERT_FALSE(box2.contains_block(-10, -12, -12));
                        ASSERT_FALSE(box2.contains_block(-10, -11, -13));
                        ASSERT_FALSE(box2.contains_block(-9, -10, -10));
                        ASSERT_FALSE(box2.contains_block(-10, -9, -10));
                        ASSERT_FALSE(box2.contains_block(-10, -10, -9));
                    },
                    py::name("test_contains_block")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(1, 2, 3, 4, 5, 6);
                        ASSERT_TRUE(box1.contains_point(1, 2, 3));
                        ASSERT_TRUE(box1.contains_point(5, 7, 9));

                        ASSERT_FALSE(box1.contains_point(0.99, 2, 3));
                        ASSERT_FALSE(box1.contains_point(1, 1.99, 3));
                        ASSERT_FALSE(box1.contains_point(1, 2, 2.99));
                        ASSERT_FALSE(box1.contains_point(5.01, 7, 9));
                        ASSERT_FALSE(box1.contains_point(5, 7.01, 9));
                        ASSERT_FALSE(box1.contains_point(5, 7, 9.01));

                        Amulet::SelectionBox box2(-10, -11, -12, 1, 2, 3);
                        ASSERT_TRUE(box2.contains_point(-10, -11, -12));
                        ASSERT_TRUE(box2.contains_point(-9, -9, -9));

                        ASSERT_FALSE(box2.contains_point(-10.01, -11, -12));
                        ASSERT_FALSE(box2.contains_point(-10, -11.01, -12));
                        ASSERT_FALSE(box2.contains_point(-10, -11, -12.01));
                        ASSERT_FALSE(box2.contains_point(-8.99, -9, -9));
                        ASSERT_FALSE(box2.contains_point(-9, -8.99, -9));
                        ASSERT_FALSE(box2.contains_point(-9, -9, -8.99));
                    },
                    py::name("test_contains_point")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(-5, -5, -5, 10, 10, 10);
                        ASSERT_TRUE(box1.contains_box(Amulet::SelectionBox(0, 0, 0, 1, 1, 1)));
                        ASSERT_TRUE(box1.contains_box(Amulet::SelectionBox(-5, -5, -5, 10, 10, 10)));

                        ASSERT_FALSE(box1.contains_box(Amulet::SelectionBox(-6, -5, -5, 10, 10, 10)));
                        ASSERT_FALSE(box1.contains_box(Amulet::SelectionBox(-5, -6, -5, 10, 10, 10)));
                        ASSERT_FALSE(box1.contains_box(Amulet::SelectionBox(-5, -5, -6, 10, 10, 10)));
                        ASSERT_FALSE(box1.contains_box(Amulet::SelectionBox(-5, -5, -5, 11, 10, 10)));
                        ASSERT_FALSE(box1.contains_box(Amulet::SelectionBox(-5, -5, -5, 10, 11, 10)));
                        ASSERT_FALSE(box1.contains_box(Amulet::SelectionBox(-5, -5, -5, 10, 10, 11)));

                        Amulet::SelectionBox box2(5, 5, 5, 10, 10, 10);
                        ASSERT_TRUE(box2.contains_box(Amulet::SelectionBox(10, 10, 10, 1, 1, 1)));
                        ASSERT_TRUE(box2.contains_box(Amulet::SelectionBox(5, 5, 5, 10, 10, 10)));

                        ASSERT_FALSE(box2.contains_box(Amulet::SelectionBox(4, 5, 5, 10, 10, 10)));
                        ASSERT_FALSE(box2.contains_box(Amulet::SelectionBox(5, 4, 5, 10, 10, 10)));
                        ASSERT_FALSE(box2.contains_box(Amulet::SelectionBox(5, 5, 4, 10, 10, 10)));
                        ASSERT_FALSE(box2.contains_box(Amulet::SelectionBox(5, 5, 5, 11, 10, 10)));
                        ASSERT_FALSE(box2.contains_box(Amulet::SelectionBox(5, 5, 5, 10, 11, 10)));
                        ASSERT_FALSE(box2.contains_box(Amulet::SelectionBox(5, 5, 5, 10, 10, 11)));
                    },
                    py::name("test_contains_box")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(-5, -5, -5, 10, 10, 10);
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBox(0, 0, 0, 1, 1, 1)));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBox(-5, -5, -5, 10, 10, 10)));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBox(-6, -5, -5, 10, 10, 10)));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBox(-5, -6, -5, 10, 10, 10)));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBox(-5, -5, -6, 10, 10, 10)));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBox(-5, -5, -5, 11, 10, 10)));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBox(-5, -5, -5, 10, 11, 10)));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBox(-5, -5, -5, 10, 10, 11)));

                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBox(-6, -5, -5, 1, 10, 10)));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBox(-5, -6, -5, 10, 1, 10)));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBox(-5, -5, -6, 10, 10, 1)));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBox(5, -5, -5, 1, 10, 10)));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBox(-5, 5, -5, 10, 1, 10)));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBox(-5, -5, 5, 10, 10, 1)));

                        Amulet::SelectionBox box2(5, 5, 5, 10, 10, 10);
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBox(10, 10, 10, 1, 1, 1)));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBox(5, 5, 5, 10, 10, 10)));

                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBox(4, 5, 5, 10, 10, 10)));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBox(5, 4, 5, 10, 10, 10)));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBox(5, 5, 4, 10, 10, 10)));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBox(5, 5, 5, 11, 10, 10)));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBox(5, 5, 5, 10, 11, 10)));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBox(5, 5, 5, 10, 10, 11)));

                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBox(4, 5, 5, 1, 10, 10)));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBox(5, 4, 5, 10, 1, 10)));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBox(5, 5, 4, 10, 10, 1)));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBox(15, 5, 5, 1, 10, 10)));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBox(5, 15, 5, 10, 1, 10)));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBox(5, 5, 15, 10, 10, 1)));
                    },
                    py::name("test_intersects_box")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(-5, -5, -5, 10, 10, 10);
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBoxGroup()));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(0, 0, 0, 1, 1, 1) })));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -5, -5, 10, 10, 10) })));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-6, -5, -5, 10, 10, 10) })));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -6, -5, 10, 10, 10) })));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -5, -6, 10, 10, 10) })));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -5, -5, 11, 10, 10) })));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -5, -5, 10, 11, 10) })));
                        ASSERT_TRUE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -5, -5, 10, 10, 11) })));

                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-6, -5, -5, 1, 10, 10) })));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -6, -5, 10, 1, 10) })));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -5, -6, 10, 10, 1) })));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, -5, -5, 1, 10, 10) })));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, 5, -5, 10, 1, 10) })));
                        ASSERT_FALSE(box1.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-5, -5, 5, 10, 10, 1) })));

                        Amulet::SelectionBox box2(5, 5, 5, 10, 10, 10);
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBoxGroup()));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 10, 10, 1, 1, 1) })));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 5, 5, 10, 10, 10) })));

                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(4, 5, 5, 10, 10, 10) })));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 4, 5, 10, 10, 10) })));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 5, 4, 10, 10, 10) })));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 5, 5, 11, 10, 10) })));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 5, 5, 10, 11, 10) })));
                        ASSERT_TRUE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 5, 5, 10, 10, 11) })));

                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(4, 5, 5, 1, 10, 10) })));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 4, 5, 10, 1, 10) })));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 5, 4, 10, 10, 1) })));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(15, 5, 5, 1, 10, 10) })));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 15, 5, 10, 1, 10) })));
                        ASSERT_FALSE(box2.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(5, 5, 15, 10, 10, 1) })));
                    },
                    py::name("test_intersects_box_group")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(-5, -5, -5, 10, 10, 10);
                        // Intersects
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(0, 0, 0, 1, 1, 1)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, -5, 10, 10, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-6, -5, -5, 10, 10, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -6, -5, 10, 10, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, -6, 10, 10, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, -5, 11, 10, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, -5, 10, 11, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, -5, 10, 10, 11)));

                        // Touches
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-6, -5, -5, 1, 10, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -6, -5, 10, 1, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, -6, 10, 10, 1)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(5, -5, -5, 1, 10, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, 5, -5, 10, 1, 10)));
                        ASSERT_TRUE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, 5, 10, 10, 1)));

                        // Not touching
                        ASSERT_FALSE(box1.touches_or_intersects(Amulet::SelectionBox(-7, -5, -5, 1, 10, 10)));
                        ASSERT_FALSE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -7, -5, 10, 1, 10)));
                        ASSERT_FALSE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, -7, 10, 10, 1)));
                        ASSERT_FALSE(box1.touches_or_intersects(Amulet::SelectionBox(6, -5, -5, 1, 10, 10)));
                        ASSERT_FALSE(box1.touches_or_intersects(Amulet::SelectionBox(-5, 6, -5, 10, 1, 10)));
                        ASSERT_FALSE(box1.touches_or_intersects(Amulet::SelectionBox(-5, -5, 6, 10, 10, 1)));

                        Amulet::SelectionBox box2(5, 5, 5, 10, 10, 10);
                        // Intersects
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(10, 10, 10, 1, 1, 1)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 5, 10, 10, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(4, 5, 5, 10, 10, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 4, 5, 10, 10, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 4, 10, 10, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 5, 11, 10, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 5, 10, 11, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 5, 10, 10, 11)));

                        // Touches
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(4, 5, 5, 1, 10, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 4, 5, 10, 1, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 4, 10, 10, 1)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(15, 5, 5, 1, 10, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 15, 5, 10, 1, 10)));
                        ASSERT_TRUE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 15, 10, 10, 1)));

                        // Not touching
                        ASSERT_FALSE(box2.touches_or_intersects(Amulet::SelectionBox(3, 5, 5, 1, 10, 10)));
                        ASSERT_FALSE(box2.touches_or_intersects(Amulet::SelectionBox(5, 3, 5, 10, 1, 10)));
                        ASSERT_FALSE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 3, 10, 10, 1)));
                        ASSERT_FALSE(box2.touches_or_intersects(Amulet::SelectionBox(16, 5, 5, 1, 10, 10)));
                        ASSERT_FALSE(box2.touches_or_intersects(Amulet::SelectionBox(5, 16, 5, 10, 1, 10)));
                        ASSERT_FALSE(box2.touches_or_intersects(Amulet::SelectionBox(5, 5, 16, 10, 10, 1)));
                    },
                    py::name("test_touches_or_intersects")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(-5, -5, -5, 10, 10, 10);
                        // Intersects
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(0, 0, 0, 1, 1, 1)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -5, -5, 10, 10, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-6, -5, -5, 10, 10, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -6, -5, 10, 10, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -5, -6, 10, 10, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -5, -5, 11, 10, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -5, -5, 10, 11, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -5, -5, 10, 10, 11)));

                        // Touches
                        ASSERT_TRUE(box1.touches(Amulet::SelectionBox(-6, -5, -5, 1, 10, 10)));
                        ASSERT_TRUE(box1.touches(Amulet::SelectionBox(-5, -6, -5, 10, 1, 10)));
                        ASSERT_TRUE(box1.touches(Amulet::SelectionBox(-5, -5, -6, 10, 10, 1)));
                        ASSERT_TRUE(box1.touches(Amulet::SelectionBox(5, -5, -5, 1, 10, 10)));
                        ASSERT_TRUE(box1.touches(Amulet::SelectionBox(-5, 5, -5, 10, 1, 10)));
                        ASSERT_TRUE(box1.touches(Amulet::SelectionBox(-5, -5, 5, 10, 10, 1)));

                        // Not touching
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-7, -5, -5, 1, 10, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -7, -5, 10, 1, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -5, -7, 10, 10, 1)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(6, -5, -5, 1, 10, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, 6, -5, 10, 1, 10)));
                        ASSERT_FALSE(box1.touches(Amulet::SelectionBox(-5, -5, 6, 10, 10, 1)));

                        Amulet::SelectionBox box2(5, 5, 5, 10, 10, 10);
                        // Intersects
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(10, 10, 10, 1, 1, 1)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 5, 5, 10, 10, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(4, 5, 5, 10, 10, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 4, 5, 10, 10, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 5, 4, 10, 10, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 5, 5, 11, 10, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 5, 5, 10, 11, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 5, 5, 10, 10, 11)));

                        // Touches
                        ASSERT_TRUE(box2.touches(Amulet::SelectionBox(4, 5, 5, 1, 10, 10)));
                        ASSERT_TRUE(box2.touches(Amulet::SelectionBox(5, 4, 5, 10, 1, 10)));
                        ASSERT_TRUE(box2.touches(Amulet::SelectionBox(5, 5, 4, 10, 10, 1)));
                        ASSERT_TRUE(box2.touches(Amulet::SelectionBox(15, 5, 5, 1, 10, 10)));
                        ASSERT_TRUE(box2.touches(Amulet::SelectionBox(5, 15, 5, 10, 1, 10)));
                        ASSERT_TRUE(box2.touches(Amulet::SelectionBox(5, 5, 15, 10, 10, 1)));

                        // Not touching
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(3, 5, 5, 1, 10, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 3, 5, 10, 1, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 5, 3, 10, 10, 1)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(16, 5, 5, 1, 10, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 16, 5, 10, 1, 10)));
                        ASSERT_FALSE(box2.touches(Amulet::SelectionBox(5, 5, 16, 10, 10, 1)));
                    },
                    py::name("test_touches")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(-5, -5, -5, 10, 10, 10);
                        auto box2 = box1.translate(1, 2, -3);
                        ASSERT_EQUAL(std::int64_t, -4, box2.min_x());
                        ASSERT_EQUAL(std::int64_t, -3, box2.min_y());
                        ASSERT_EQUAL(std::int64_t, -8, box2.min_z());
                        ASSERT_EQUAL(std::int64_t, 6, box2.max_x());
                        ASSERT_EQUAL(std::int64_t, 7, box2.max_y());
                        ASSERT_EQUAL(std::int64_t, 2, box2.max_z());
                    },
                    py::name("test_translate")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box1(1, 2, 3, 10, 10, 10);

                        // Transform by the identity matrix
                        auto group1 = box1.transform(Amulet::Matrix4x4());
                        ASSERT_EQUAL(size_t, 1, group1.count());
                        const auto& box2 = *group1.get_boxes().begin();
                        ASSERT_EQUAL(std::int64_t, 1, box2.min_x());
                        ASSERT_EQUAL(std::int64_t, 2, box2.min_y());
                        ASSERT_EQUAL(std::int64_t, 3, box2.min_z());
                        ASSERT_EQUAL(std::int64_t, 11, box2.max_x());
                        ASSERT_EQUAL(std::int64_t, 12, box2.max_y());
                        ASSERT_EQUAL(std::int64_t, 13, box2.max_z());

                        // Transform by a multple of 90 degrees
                        auto group2 = box1.transform(Amulet::Matrix4x4::rotation_y_matrix(std::numbers::pi / 2));
                        ASSERT_EQUAL(size_t, 1, group2.count());
                        const auto& box3 = *group2.get_boxes().begin();
                        ASSERT_EQUAL(std::int64_t, 3, box3.min_x());
                        ASSERT_EQUAL(std::int64_t, 2, box3.min_y());
                        ASSERT_EQUAL(std::int64_t, -11, box3.min_z());
                        ASSERT_EQUAL(std::int64_t, 13, box3.max_x());
                        ASSERT_EQUAL(std::int64_t, 12, box3.max_y());
                        ASSERT_EQUAL(std::int64_t, -1, box3.max_z());

                        // Transform complex
                        auto group3 = box1.transform(Amulet::Matrix4x4::rotation_y_matrix(std::numbers::pi / 4));
                        ASSERT_LESS(size_t, 10, group3.count());
                    },
                    py::name("test_transform")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box(1, 2, 3, 4, 5, 6);

                        ASSERT_EQUAL(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 3, 4, 5, 6));
                        ASSERT_NOT_EQUAL(Amulet::SelectionBox, box, Amulet::SelectionBox(11, 2, 3, 4, 5, 6));
                        ASSERT_NOT_EQUAL(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 12, 3, 4, 5, 6));
                        ASSERT_NOT_EQUAL(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 13, 4, 5, 6));
                        ASSERT_NOT_EQUAL(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 3, 14, 5, 6));
                        ASSERT_NOT_EQUAL(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 3, 4, 15, 6));
                        ASSERT_NOT_EQUAL(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 3, 4, 5, 16));
                    },
                    py::name("test_equal")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBox box(1, 2, 3, 4, 5, 6);

                        ASSERT_LESS(Amulet::SelectionBox, box, Amulet::SelectionBox(2, 2, 3, 4, 5, 6));
                        ASSERT_LESS(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 3, 3, 4, 5, 6));
                        ASSERT_LESS(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 4, 4, 5, 6));
                        ASSERT_LESS(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 3, 5, 5, 6));
                        ASSERT_LESS(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 3, 4, 6, 6));
                        ASSERT_LESS(Amulet::SelectionBox, box, Amulet::SelectionBox(1, 2, 3, 4, 5, 7));
                    },
                    py::name("test_compare")));

            return tests;
        });
}

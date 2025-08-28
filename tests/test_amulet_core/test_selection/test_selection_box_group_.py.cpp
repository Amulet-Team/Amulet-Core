#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <numbers>

#include <amulet/test_utils/test_utils.hpp>

#include <amulet/utils/matrix.hpp>

#include <amulet/core/selection/box.hpp>
#include <amulet/core/selection/box_group.hpp>

namespace py = pybind11;

void init_test_selection_box_group(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_selection_box_group_");

    m.def(
        "get_tests",
        []() -> py::typing::List<py::typing::Callable<void()>> {
            py::list tests;

            tests.append(
                py::cpp_function(
                    []() {
                        std::set<Amulet::SelectionBox> boxes {
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        };
                        Amulet::SelectionBoxGroup group(boxes);
                        ASSERT_EQUAL(size_t, 2, group.count());
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes, group.get_boxes());
                    },
                    py::name("test_constructor_set_copy")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::list<Amulet::SelectionBox> boxes {
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        };
                        std::set<Amulet::SelectionBox> boxes_expected {
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        };
                        Amulet::SelectionBoxGroup group(boxes.begin(), boxes.end());
                        ASSERT_EQUAL(size_t, 2, group.count());
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_constructor_iterator")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::set<Amulet::SelectionBox> boxes_expected {
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        };
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        ASSERT_EQUAL(size_t, 2, group.count());
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_constructor_initialiser_list")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::set<Amulet::SelectionBox> boxes_expected {
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        };
                        Amulet::SelectionBoxGroup group1({
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        Amulet::SelectionBoxGroup group2(group1);
                        ASSERT_EQUAL(size_t, 2, group1.count());
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group1.get_boxes());
                        ASSERT_EQUAL(size_t, 2, group2.count());
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group2.get_boxes());
                    },
                    py::name("test_constructor_copy")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::set<Amulet::SelectionBox> boxes_expected {
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        };
                        Amulet::SelectionBoxGroup group1({
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        Amulet::SelectionBoxGroup group2(std::move(group1));
                        ASSERT_EQUAL(size_t, 0, group1.count());
                        ASSERT_EQUAL(size_t, 2, group2.count());
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group2.get_boxes());
                    },
                    py::name("test_constructor_move")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::set<Amulet::SelectionBox> boxes_expected {
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        };
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, group.get_boxes());
                    },
                    py::name("test_get_boxes")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        ASSERT_EQUAL(size_t, 2, group.count());
                    },
                    py::name("test_get_count")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::set<Amulet::SelectionBox> boxes_expected {
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        };
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(1, 2, 3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        std::set<Amulet::SelectionBox> boxes;
                        for (const auto& box : group) {
                            boxes.insert(box);
                        }
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, boxes);
                    },
                    py::name("test_iterator")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(-1, -2, -3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        ASSERT_EQUAL(std::int64_t, -1, group.min_x());
                        ASSERT_EQUAL(std::int64_t, -2, group.min_y());
                        ASSERT_EQUAL(std::int64_t, -3, group.min_z());
                        ASSERT_EQUAL(std::int64_t, 17, group.max_x());
                        ASSERT_EQUAL(std::int64_t, 19, group.max_y());
                        ASSERT_EQUAL(std::int64_t, 21, group.max_z());

                        ASSERT_EQUAL(std::int64_t, -1, group.min()[0]);
                        ASSERT_EQUAL(std::int64_t, -2, group.min()[1]);
                        ASSERT_EQUAL(std::int64_t, -3, group.min()[2]);
                        ASSERT_EQUAL(std::int64_t, 17, group.max()[0]);
                        ASSERT_EQUAL(std::int64_t, 19, group.max()[1]);
                        ASSERT_EQUAL(std::int64_t, 21, group.max()[2]);

                        ASSERT_EQUAL(std::int64_t, -1, group.bounds().first[0]);
                        ASSERT_EQUAL(std::int64_t, -2, group.bounds().first[1]);
                        ASSERT_EQUAL(std::int64_t, -3, group.bounds().first[2]);
                        ASSERT_EQUAL(std::int64_t, 17, group.bounds().second[0]);
                        ASSERT_EQUAL(std::int64_t, 19, group.bounds().second[1]);
                        ASSERT_EQUAL(std::int64_t, 21, group.bounds().second[2]);

                        ASSERT_EQUAL(Amulet::SelectionBox, Amulet::SelectionBox(-1, -2, -3, 18, 21, 24), group.bounding_box());
                    },
                    py::name("test_bounds")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(-1, -2, -3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        ASSERT_TRUE(group.contains_block(-1, -2, -3));
                        ASSERT_TRUE(group.contains_block(2, 2, 2));
                        ASSERT_TRUE(group.contains_block(7, 8, 9));
                        ASSERT_TRUE(group.contains_block(16, 18, 20));

                        ASSERT_FALSE(group.contains_block(-2, -2, -3));
                        ASSERT_FALSE(group.contains_block(-1, -3, -3));
                        ASSERT_FALSE(group.contains_block(-1, -2, -4));
                        ASSERT_FALSE(group.contains_block(3, 2, 2));
                        ASSERT_FALSE(group.contains_block(2, 3, 2));
                        ASSERT_FALSE(group.contains_block(2, 2, 3));
                        ASSERT_FALSE(group.contains_block(6, 8, 9));
                        ASSERT_FALSE(group.contains_block(7, 7, 9));
                        ASSERT_FALSE(group.contains_block(7, 8, 8));
                        ASSERT_FALSE(group.contains_block(17, 18, 20));
                        ASSERT_FALSE(group.contains_block(16, 19, 20));
                        ASSERT_FALSE(group.contains_block(16, 18, 21));
                    },
                    py::name("test_contains_block")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(-1, -2, -3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        ASSERT_TRUE(group.contains_point(-1, -2, -3));
                        ASSERT_TRUE(group.contains_point(3, 3, 3));
                        ASSERT_TRUE(group.contains_point(7, 8, 9));
                        ASSERT_TRUE(group.contains_point(17, 19, 21));

                        ASSERT_FALSE(group.contains_point(-1.01, -2, -3));
                        ASSERT_FALSE(group.contains_point(-1, -2.01, -3));
                        ASSERT_FALSE(group.contains_point(-1, -2, -3.01));
                        ASSERT_FALSE(group.contains_point(3.01, 3, 3));
                        ASSERT_FALSE(group.contains_point(3, 3.01, 3));
                        ASSERT_FALSE(group.contains_point(3, 3, 3.01));
                        ASSERT_FALSE(group.contains_point(6.99, 8, 9));
                        ASSERT_FALSE(group.contains_point(7, 7.99, 9));
                        ASSERT_FALSE(group.contains_point(7, 8, 8.99));
                        ASSERT_FALSE(group.contains_point(17.01, 19, 21));
                        ASSERT_FALSE(group.contains_point(17, 19.01, 21));
                        ASSERT_FALSE(group.contains_point(17, 19, 21.01));
                    },
                    py::name("test_contains_point")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(-1, -2, -3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        ASSERT_TRUE(group.intersects(Amulet::SelectionBox(-1, -2, -3, 1, 1, 1)));
                        ASSERT_TRUE(group.intersects(Amulet::SelectionBox(2, 2, 2, 1, 1, 1)));
                        ASSERT_TRUE(group.intersects(Amulet::SelectionBox(7, 8, 9, 1, 1, 1)));
                        ASSERT_TRUE(group.intersects(Amulet::SelectionBox(16, 18, 20, 1, 1, 1)));

                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(-2, -2, -3, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(-1, -3, -3, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(-1, -2, -4, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(3, 2, 2, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(2, 3, 2, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(2, 2, 3, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(6, 8, 9, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(7, 7, 9, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(7, 8, 8, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(17, 18, 20, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(16, 19, 20, 1, 1, 1)));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBox(16, 18, 21, 1, 1, 1)));
                    },
                    py::name("test_intesects_box")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(-1, -2, -3, 4, 5, 6),
                            Amulet::SelectionBox(7, 8, 9, 10, 11, 12),
                        });
                        ASSERT_TRUE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-1, -2, -3, 1, 1, 1) })));
                        ASSERT_TRUE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(2, 2, 2, 1, 1, 1) })));
                        ASSERT_TRUE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(7, 8, 9, 1, 1, 1) })));
                        ASSERT_TRUE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(16, 18, 20, 1, 1, 1) })));

                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-2, -2, -3, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-1, -3, -3, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(-1, -2, -4, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(3, 2, 2, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(2, 3, 2, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(2, 2, 3, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(6, 8, 9, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(7, 7, 9, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(7, 8, 8, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(17, 18, 20, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(16, 19, 20, 1, 1, 1) })));
                        ASSERT_FALSE(group.intersects(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(16, 18, 21, 1, 1, 1) })));
                    },
                    py::name("test_intesects_box_group")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group1({
                            Amulet::SelectionBox(10, 20, 30, 1, 1, 1),
                        });
                        auto group2 = group1.translate(100, 200, 300);
                        ASSERT_EQUAL(size_t, 1, group2.count());
                        ASSERT_EQUAL(Amulet::SelectionBox, Amulet::SelectionBox(110, 220, 330, 1, 1, 1), *group2.begin());
                    },
                    py::name("test_translate")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group1({
                            Amulet::SelectionBox(10, 20, 30, 10, 20, 30),
                        });
                        auto group2 = group1.transform(Amulet::Matrix4x4::rotation_y_matrix(std::numbers::pi / 2));
                        ASSERT_EQUAL(size_t, 1, group2.count());
                        ASSERT_EQUAL(Amulet::SelectionBox, Amulet::SelectionBox(30, 20, -20, 30, 20, 10), *group2.begin());
                    },
                    py::name("test_translate_90")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group1({
                            Amulet::SelectionBox(10, 20, 30, 10, 20, 30),
                        });
                        auto group2 = group1.transform(Amulet::Matrix4x4::rotation_y_matrix(std::numbers::pi / 4));
                        ASSERT_LESS(size_t, 10, group2.count());
                    },
                    py::name("test_translate_45")));

            tests.append(
                py::cpp_function(
                    []() {
                        ASSERT_FALSE(Amulet::SelectionBoxGroup());
                        ASSERT_TRUE(Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 20, 30, 10, 20, 30) }));
                    },
                    py::name("test_operator_bool")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group1;
                        Amulet::SelectionBoxGroup group2({ Amulet::SelectionBox(10, 20, 30, 10, 20, 30) });
                        ASSERT_EQUAL(const Amulet::SelectionBoxGroup, group1, Amulet::SelectionBoxGroup());
                        ASSERT_EQUAL(const Amulet::SelectionBoxGroup, group2, Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 20, 30, 10, 20, 30) }));
                        ASSERT_NOT_EQUAL(const Amulet::SelectionBoxGroup, group1, Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 20, 30, 10, 20, 30) }));
                        ASSERT_NOT_EQUAL(const Amulet::SelectionBoxGroup, group2, Amulet::SelectionBoxGroup());
                        ASSERT_NOT_EQUAL(const Amulet::SelectionBoxGroup, group2, Amulet::SelectionBoxGroup({ Amulet::SelectionBox(11, 20, 30, 10, 20, 30) }));
                        ASSERT_NOT_EQUAL(const Amulet::SelectionBoxGroup, group2, Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 21, 30, 10, 20, 30) }));
                        ASSERT_NOT_EQUAL(const Amulet::SelectionBoxGroup, group2, Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 20, 31, 10, 20, 30) }));
                        ASSERT_NOT_EQUAL(const Amulet::SelectionBoxGroup, group2, Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 20, 30, 11, 20, 30) }));
                        ASSERT_NOT_EQUAL(const Amulet::SelectionBoxGroup, group2, Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 20, 30, 10, 21, 30) }));
                        ASSERT_NOT_EQUAL(const Amulet::SelectionBoxGroup, group2, Amulet::SelectionBoxGroup({ Amulet::SelectionBox(10, 20, 30, 10, 20, 31) }));
                    },
                    py::name("test_operator_equal")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group1;
                        Amulet::SelectionBoxGroup group2({ Amulet::SelectionBox(10, 20, 30, 10, 20, 30) });
                        ASSERT_LESS(const Amulet::SelectionBoxGroup, group1, group2);
                        ASSERT_LESS_EQUAL(const Amulet::SelectionBoxGroup, group1, group2);
                        ASSERT_LESS_EQUAL(const Amulet::SelectionBoxGroup, group1, group1);
                        ASSERT_LESS_EQUAL(const Amulet::SelectionBoxGroup, group2, group2);
                        ASSERT_GREATER(const Amulet::SelectionBoxGroup, group2, group1);
                        ASSERT_GREATER_EQUAL(const Amulet::SelectionBoxGroup, group2, group1);
                        ASSERT_GREATER_EQUAL(const Amulet::SelectionBoxGroup, group1, group1);
                        ASSERT_GREATER_EQUAL(const Amulet::SelectionBoxGroup, group2, group2);
                    },
                    py::name("test_operator_compare")));

            tests.append(
                py::cpp_function(
                    []() {
                        Amulet::SelectionBoxGroup group({
                            Amulet::SelectionBox(10, 20, 30, 10, 20, 30),
                            Amulet::SelectionBox(110, 120, 130, 10, 20, 30),
                        });
                        std::set<Amulet::SelectionBox> boxes = group;
                        std::set<Amulet::SelectionBox> boxes_expected {
                            Amulet::SelectionBox(10, 20, 30, 10, 20, 30),
                            Amulet::SelectionBox(110, 120, 130, 10, 20, 30),
                        };
                        ASSERT_EQUAL(const std::set<Amulet::SelectionBox>&, boxes_expected, boxes);
                    },
                    py::name("test_operator_set")));

            return tests;
        });
}

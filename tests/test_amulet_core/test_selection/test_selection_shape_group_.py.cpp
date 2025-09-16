#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <memory>

#include <amulet/test_utils/test_utils.hpp>

#include <amulet/core/selection/box_group.hpp>
#include <amulet/core/selection/cuboid.hpp>
#include <amulet/core/selection/ellipsoid.hpp>
#include <amulet/core/selection/shape_group.hpp>

namespace py = pybind11;

void init_test_selection_shape_group(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_selection_shape_group_");

    m.def(
        "get_tests",
        []() -> py::typing::List<py::typing::Callable<void()>> {
            py::list tests;

            tests.append(
                py::cpp_function(
                    []() {
                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));

                        Amulet::SelectionShapeGroup group(std::move(shapes));
                        ASSERT_EQUAL(size_t, 2, group.count());

                        auto it = group.begin();
                        auto* cuboid = dynamic_cast<Amulet::SelectionCuboid*>(it->get());
                        ASSERT_TRUE(cuboid);
                        ASSERT_TRUE(cuboid->almost_equal(Amulet::SelectionCuboid(1, 2, 3, 4, 5, 6)));

                        it++;
                        auto* ellipsoid = dynamic_cast<Amulet::SelectionEllipsoid*>(it->get());
                        ASSERT_TRUE(ellipsoid);
                        ASSERT_TRUE(ellipsoid->almost_equal(Amulet::SelectionEllipsoid(1, 2, 3, 4)));
                    },
                    py::name("test_constructor_vector_move")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));

                        Amulet::SelectionShapeGroup group1(std::move(shapes));
                        Amulet::SelectionShapeGroup group2(std::move(group1));
                        ASSERT_EQUAL(size_t, 2, group2.count());

                        auto it = group2.begin();
                        auto* cuboid = dynamic_cast<Amulet::SelectionCuboid*>(it->get());
                        ASSERT_TRUE(cuboid);
                        ASSERT_TRUE(cuboid->almost_equal(Amulet::SelectionCuboid(1, 2, 3, 4, 5, 6)));

                        it++;
                        auto* ellipsoid = dynamic_cast<Amulet::SelectionEllipsoid*>(it->get());
                        ASSERT_TRUE(ellipsoid);
                        ASSERT_TRUE(ellipsoid->almost_equal(Amulet::SelectionEllipsoid(1, 2, 3, 4)));
                    },
                    py::name("test_constructor_move")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));

                        Amulet::SelectionShapeGroup group(std::move(shapes));
                        const auto& shapes_view = group.get_shapes();
                        ASSERT_EQUAL(size_t, 2, shapes_view.size());

                        auto it = shapes_view.begin();
                        auto* cuboid = dynamic_cast<Amulet::SelectionCuboid*>(it->get());
                        ASSERT_TRUE(cuboid);
                        ASSERT_TRUE(cuboid->almost_equal(Amulet::SelectionCuboid(1, 2, 3, 4, 5, 6)));

                        it++;
                        auto* ellipsoid = dynamic_cast<Amulet::SelectionEllipsoid*>(it->get());
                        ASSERT_TRUE(ellipsoid);
                        ASSERT_TRUE(ellipsoid->almost_equal(Amulet::SelectionEllipsoid(1, 2, 3, 4)));
                    },
                    py::name("test_get_shapes")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));

                        Amulet::SelectionShapeGroup group(std::move(shapes));
                        ASSERT_EQUAL(size_t, 2, group.count());

                        auto it = group.begin();
                        auto* cuboid = dynamic_cast<Amulet::SelectionCuboid*>(it->get());
                        ASSERT_TRUE(cuboid);
                        ASSERT_TRUE(cuboid->almost_equal(Amulet::SelectionCuboid(1, 2, 3, 4, 5, 6)));

                        it++;
                        auto* ellipsoid = dynamic_cast<Amulet::SelectionEllipsoid*>(it->get());
                        ASSERT_TRUE(ellipsoid);
                        ASSERT_TRUE(ellipsoid->almost_equal(Amulet::SelectionEllipsoid(1, 2, 3, 4)));
                    },
                    py::name("test_iterator")));

            tests.append(
                py::cpp_function(
                    []() {
                        ASSERT_FALSE(Amulet::SelectionShapeGroup());

                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        ASSERT_TRUE(Amulet::SelectionShapeGroup(std::move(shapes)));
                    },
                    py::name("test_operator_bool")));

            tests.append(
                py::cpp_function(
                    []() {
                        ASSERT_EQUAL(size_t, 0, Amulet::SelectionShapeGroup().count());
                        {
                            std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                            shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                            Amulet::SelectionShapeGroup group(std::move(shapes));
                            ASSERT_EQUAL(size_t, 1, group.count());
                        }
                        {
                            std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                            shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                            shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));
                            Amulet::SelectionShapeGroup group(std::move(shapes));
                            ASSERT_EQUAL(size_t, 2, group.count());
                        }
                    },
                    py::name("test_count")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));

                        Amulet::SelectionShapeGroup shape_group(std::move(shapes));

                        auto box_group = static_cast<Amulet::SelectionBoxGroup>(shape_group);
                        ASSERT_LESS(size_t, 10, box_group.count());
                    },
                    py::name("test_operator_box_group")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));

                        Amulet::SelectionShapeGroup shape_group(std::move(shapes));

                        auto box_group = static_cast<std::set<Amulet::SelectionBox>>(shape_group);
                        ASSERT_LESS(size_t, 10, box_group.size());
                    },
                    py::name("test_operator_set_box")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));

                        Amulet::SelectionShapeGroup shape_group(std::move(shapes));

                        auto box_group = shape_group.voxelise();
                        ASSERT_LESS(size_t, 10, box_group.count());
                    },
                    py::name("test_voxelise")));

            tests.append(
                py::cpp_function(
                    []() {
                        std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;

                        Amulet::SelectionShapeGroup group_empty_1;
                        Amulet::SelectionShapeGroup group_empty_2;
                        ASSERT_TRUE(group_empty_1.almost_equal(group_empty_2));

                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        Amulet::SelectionShapeGroup group_3(std::move(shapes));
                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 6));
                        Amulet::SelectionShapeGroup group_4(std::move(shapes));
                        ASSERT_TRUE(group_3.almost_equal(group_4));
                        ASSERT_FALSE(group_empty_1.almost_equal(group_3));
                        ASSERT_FALSE(group_3.almost_equal(group_empty_1));

                        shapes.push_back(std::make_unique<Amulet::SelectionEllipsoid>(1, 2, 3, 4));
                        Amulet::SelectionShapeGroup group_5(std::move(shapes));
                        ASSERT_FALSE(group_3.almost_equal(group_5));
                        ASSERT_FALSE(group_5.almost_equal(group_3));

                        shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(1, 2, 3, 4, 5, 7));
                        Amulet::SelectionShapeGroup group_6(std::move(shapes));
                        ASSERT_FALSE(group_3.almost_equal(group_6));
                        ASSERT_FALSE(group_6.almost_equal(group_3));
                    },
                    py::name("test_almost_equal")));

            return tests;
        });
}

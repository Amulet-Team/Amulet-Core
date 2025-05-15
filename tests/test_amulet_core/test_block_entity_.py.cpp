#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <functional>
#include <string>
#include <string_view>
#include <vector>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/test_utils/test_utils.hpp>

#include <amulet/core/block_entity/block_entity.hpp>
#include <amulet/core/version/version.hpp>

namespace py = pybind11;

static void test_ctror_attrs_lvalue()
{
}

static void test_ctror_attrs_rvalue()
{
}

static void test_ctror_attrs_view()
{
}

static void test_get_set()
{
}

static void test_equal()
{
}

static void test_compare()
{
}

static void test_serialise()
{
}

#define add_test(test_name) tests.push_back({ #test_name, test_name });

static std::vector<std::pair<std::string, std::function<void()>>> get_tests()
{
    std::vector<std::pair<std::string, std::function<void()>>> tests;

    add_test(test_ctror_attrs_lvalue);
    add_test(test_ctror_attrs_rvalue);
    add_test(test_ctror_attrs_view);
    add_test(test_get_set);
    add_test(test_equal);
    add_test(test_compare);
    add_test(test_serialise);

    return tests;
}

void init_test_block_entity(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_block_entity_");
    m.def("get_tests", &get_tests);
}

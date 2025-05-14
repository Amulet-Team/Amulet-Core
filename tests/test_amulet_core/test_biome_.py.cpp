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

#include <amulet/core/biome/biome.hpp>
#include <amulet/core/version/version.hpp>

namespace py = pybind11;

#define VersionTuple { 1, 2, 3 }

static void test_ctror_attrs_lvalue()
{
    Amulet::PlatformType biome_platform = "java";
    Amulet::VersionNumber biome_version = { 1, 2, 3 };
    std::string biome_namespace = "hello";
    std::string biome_base_name = "world";

    Amulet::Biome biome_lvalue(biome_platform, biome_version, biome_namespace, biome_base_name);

    ASSERT_EQUAL(std::string, "java", biome_lvalue.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, biome_lvalue.get_version());
    ASSERT_EQUAL(std::string, "hello", biome_lvalue.get_namespace());
    ASSERT_EQUAL(std::string, "world", biome_lvalue.get_base_name());
}

static void test_ctror_attrs_rvalue()
{
    Amulet::Biome biome_rvalue("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");

    ASSERT_EQUAL(std::string, "java", biome_rvalue.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, biome_rvalue.get_version());
    ASSERT_EQUAL(std::string, "hello", biome_rvalue.get_namespace());
    ASSERT_EQUAL(std::string, "world", biome_rvalue.get_base_name());
}

static void test_ctror_attrs_view()
{
    Amulet::PlatformType biome_platform = "java";
    Amulet::VersionNumber biome_version = { 1, 2, 3 };
    std::string biome_namespace = "hello";
    std::string biome_base_name = "world";

    std::string_view biome_platform_view = biome_platform;
    std::string_view biome_namespace_view = biome_namespace;
    std::string_view biome_base_name_view = biome_base_name;

    Amulet::Biome biome_lvalue(biome_platform_view, biome_version, biome_namespace_view, biome_base_name_view);

    ASSERT_EQUAL(std::string, "java", biome_lvalue.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, biome_lvalue.get_version());
    ASSERT_EQUAL(std::string, "hello", biome_lvalue.get_namespace());
    ASSERT_EQUAL(std::string, "world", biome_lvalue.get_base_name());
}

static void test_equal()
{
    Amulet::Biome biome_1("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Biome biome_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Biome biome_3("java_", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Biome biome_4("java", Amulet::VersionNumber { 0, 2, 3 }, "hello", "world");
    Amulet::Biome biome_5("java", Amulet::VersionNumber { 1, 3, 3 }, "hello", "world");
    Amulet::Biome biome_6("java", Amulet::VersionNumber { 1, 2, 4 }, "hello", "world");
    Amulet::Biome biome_7("java", Amulet::VersionNumber { 1, 2, 3 }, "hello_", "world");
    Amulet::Biome biome_8("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world_");
    ASSERT_EQUAL(Amulet::Biome, biome_1, biome_2);
    ASSERT_NOT_EQUAL(Amulet::Biome, biome_1, biome_3);
    ASSERT_NOT_EQUAL(Amulet::Biome, biome_1, biome_4);
    ASSERT_NOT_EQUAL(Amulet::Biome, biome_1, biome_5);
    ASSERT_NOT_EQUAL(Amulet::Biome, biome_1, biome_6);
    ASSERT_NOT_EQUAL(Amulet::Biome, biome_1, biome_7);
    ASSERT_NOT_EQUAL(Amulet::Biome, biome_1, biome_8);
}

static void test_compare()
{
    Amulet::Biome biome_1("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Biome biome_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Biome biome_3("java_", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Biome biome_4("java", Amulet::VersionNumber { 0, 2, 3 }, "hello", "world");
    Amulet::Biome biome_5("java", Amulet::VersionNumber { 1, 3, 3 }, "hello", "world");
    Amulet::Biome biome_6("java", Amulet::VersionNumber { 1, 2, 4 }, "hello", "world");
    Amulet::Biome biome_7("java", Amulet::VersionNumber { 1, 2, 3 }, "hello_", "world");
    Amulet::Biome biome_8("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world_");

    ASSERT_EQUAL(Amulet::Biome, biome_1, biome_2);
    ASSERT_GREATER_EQUAL(Amulet::Biome, biome_1, biome_2);
    ASSERT_LESS_EQUAL(Amulet::Biome, biome_1, biome_2);

    ASSERT_LESS(Amulet::Biome, biome_1, biome_3);
    ASSERT_GREATER(Amulet::Biome, biome_1, biome_4);
    ASSERT_LESS(Amulet::Biome, biome_1, biome_5);
    ASSERT_LESS(Amulet::Biome, biome_1, biome_6);
    ASSERT_LESS(Amulet::Biome, biome_1, biome_7);
    ASSERT_LESS(Amulet::Biome, biome_1, biome_8);
}

static void test_serialise()
{
    Amulet::Biome biome("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    std::string encoded("\x01\x04\x00\x00\x00\x00\x00\x00\x00java\x01\x03\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00hello\x05\x00\x00\x00\x00\x00\x00\x00world", 72);

    ASSERT_EQUAL(std::string, encoded, Amulet::serialise(biome))
    ASSERT_EQUAL(Amulet::Biome, biome, Amulet::deserialise<Amulet::Biome>(encoded))
}

#define add_test(test_name) tests.push_back({ #test_name, test_name });

static std::vector<std::pair<std::string, std::function<void()>>> get_tests()
{
    std::vector<std::pair<std::string, std::function<void()>>> tests;

    add_test(test_ctror_attrs_lvalue);
    add_test(test_ctror_attrs_rvalue);
    add_test(test_ctror_attrs_view);
    add_test(test_equal);
    add_test(test_compare);
    add_test(test_serialise);

    return tests;
}

void init_test_biome(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_biome_");

    m.def("get_tests", &get_tests);
}

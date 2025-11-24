#include <pybind11/pybind11.h>

#include <amulet/core/version/version.hpp>

#include <amulet/test_utils/test_utils.hpp>

namespace py = pybind11;

static const std::vector<std::int64_t> vec5_global { 10, 11, 12, 20, 21 };
static const std::vector<std::int64_t> vec3_global { 5, 6, 7 };

static void test_version_number()
{
    Amulet::VersionNumber v0;
    ASSERT_EQUAL(size_t, 0, v0.size());

    Amulet::VersionNumber v1 { 5 };
    ASSERT_EQUAL(size_t, 1, v1.size());

    Amulet::VersionNumber v5 { 10, 11, 12, 20, 21 };
    ASSERT_EQUAL(size_t, 5, v5.size());
    ASSERT_EQUAL(std::vector<std::int64_t>, vec5_global, v5.get_vector());

    std::vector<std::int64_t> vec = vec5_global;

    // Copy construct from vector
    Amulet::VersionNumber copy_vector(vec);
    ASSERT_EQUAL(std::vector<std::int64_t>, vec5_global, vec);
    ASSERT_EQUAL(std::vector<std::int64_t>, vec5_global, copy_vector.get_vector());

    // Move construct from vector
    Amulet::VersionNumber move_vector(std::move(vec));
    ASSERT_EQUAL(std::vector<std::int64_t>, {}, vec);
    ASSERT_EQUAL(std::vector<std::int64_t>, vec5_global, move_vector.get_vector());

    // Copy construct from version
    Amulet::VersionNumber copy_version(move_vector);
    ASSERT_EQUAL(std::vector<std::int64_t>, vec5_global, move_vector.get_vector());
    ASSERT_EQUAL(std::vector<std::int64_t>, vec5_global, copy_version.get_vector());

    // Move construct from version
    Amulet::VersionNumber move_version(std::move(move_vector));
    ASSERT_EQUAL(std::vector<std::int64_t>, {}, move_vector.get_vector());
    ASSERT_EQUAL(std::vector<std::int64_t>, vec5_global, move_version.get_vector());

    vec = vec3_global;

    // Copy assign from vector
    copy_vector = vec;
    ASSERT_EQUAL(std::vector<std::int64_t>, vec3_global, vec);
    ASSERT_EQUAL(std::vector<std::int64_t>, vec3_global, copy_vector.get_vector());

    // Move assign from vector
    move_vector = std::move(vec);
    ASSERT_EQUAL(std::vector<std::int64_t>, {}, vec);
    ASSERT_EQUAL(std::vector<std::int64_t>, vec3_global, move_vector.get_vector());

    // Copy assign from version
    copy_version = move_vector;
    ASSERT_EQUAL(std::vector<std::int64_t>, vec3_global, move_vector.get_vector());
    ASSERT_EQUAL(std::vector<std::int64_t>, vec3_global, copy_version.get_vector());

    // Move assign from version
    move_version = std::move(move_vector);
    ASSERT_EQUAL(std::vector<std::int64_t>, {}, move_vector.get_vector());
    ASSERT_EQUAL(std::vector<std::int64_t>, vec3_global, move_version.get_vector());

    // TODO: Add more tests
}

static void test_version_range()
{
    // TODO: Add tests
}

void init_test_version(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_version_");
    m.def("test_version_number", &test_version_number);
    m.def("test_version_range", &test_version_range);
}

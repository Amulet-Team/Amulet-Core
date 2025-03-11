#include <pybind11/pybind11.h>

#include <amulet/level/abc/history.hpp>

namespace py = pybind11;

class TestResourceId {
private:
    std::string key;

public:
    TestResourceId(const std::string& key)
        : key(key) {};
    auto operator<=>(const TestResourceId&) const = default;
    operator std::string() const
    {
        return key;
    }
};

template <typename T>
void assert_equal(const T& a, const T& b, size_t line)
{
    if (a != b) {
        throw std::runtime_error("Values are not equal. Line: " + std::to_string(line));
    }
}

#define ASSERT_EQUAL(CLS, A, B)                                                                                    \
    {                                                                                                              \
        CLS a;                                                                                                     \
        try {                                                                                                      \
            a = A;                                                                                                 \
        } catch (const std::exception& e) {                                                                        \
            throw std::runtime_error("Failed evaluating A at line " + std::to_string(__LINE__) + ". " + e.what()); \
        }                                                                                                          \
        CLS b;                                                                                                     \
        try {                                                                                                      \
            b = B;                                                                                                 \
        } catch (const std::exception& e) {                                                                        \
            throw std::runtime_error("Failed evaluating B at line " + std::to_string(__LINE__) + ". " + e.what()); \
        }                                                                                                          \
        if (a != b) {                                                                                              \
            throw std::runtime_error("Values are not equal. Line: " + std::to_string(__LINE__));                   \
        }                                                                                                          \
    }

void init_test_history(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_history_");
    m.def("test_history", []() {
        // Create the history manager.
        Amulet::HistoryManager history_manager;

        // Create two layers.
        auto layer_1 = history_manager.new_layer<TestResourceId>();
        auto layer_2 = history_manager.new_layer<TestResourceId>();

        // Create two keys.
        TestResourceId key_1("key_1");
        TestResourceId key_2("key_2");

        // Set initial values.
        layer_1->set_initial_value(key_1, "value_1_1");
        layer_1->set_initial_value(key_2, "value_1_2");
        layer_2->set_initial_value(key_1, "value_2_1");
        layer_2->set_initial_value(key_2, "value_2_2");

        // Get initial values.
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2));
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_2_2", layer_2->get_value(key_2));

        // Create a new undo point.
        history_manager.create_undo_bin();

        // Overwrite values
        layer_1->set_value(key_2, "value_1_2b");
        layer_2->set_value(key_2, "value_2_2b");

        // Set new values
        TestResourceId key_3("key_3");
        layer_1->set_initial_value(key_3, "value_1_3");
        layer_2->set_initial_value(key_3, "value_2_3");

        // Validate
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_1_2b", layer_1->get_value(key_2));
        ASSERT_EQUAL(std::string, "value_1_3", layer_1->get_value(key_3));
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_2_2b", layer_2->get_value(key_2));
        ASSERT_EQUAL(std::string, "value_2_3", layer_2->get_value(key_3));

        // Undo and validate
        history_manager.undo();
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2));
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_2_2", layer_2->get_value(key_2));

        // Redo and validate
        history_manager.redo();
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_1_2b", layer_1->get_value(key_2));
        ASSERT_EQUAL(std::string, "value_1_3", layer_1->get_value(key_3));
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_2_2b", layer_2->get_value(key_2));
        ASSERT_EQUAL(std::string, "value_2_3", layer_2->get_value(key_3));

        // Undo and create a new undo point
        history_manager.undo();
        history_manager.create_undo_bin();

        // Validate
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2));
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1));
        ASSERT_EQUAL(std::string, "value_2_2", layer_2->get_value(key_2));
    });
}

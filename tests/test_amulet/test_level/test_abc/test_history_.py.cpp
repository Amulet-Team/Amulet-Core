#include <pybind11/pybind11.h>

#include <amulet/level/abc/history.hpp>

namespace py = pybind11;

class TestResourceId {
private:
    std::string key;

public:
    TestResourceId(const std::string& key)
        : key(key) { };
    auto operator<=>(const TestResourceId&) const = default;
    operator std::string() const
    {
        return key;
    }
};

template <typename T>
void assert_equal(const T& a, const T& b, const std::string& msg) {
    if (a != b) {
        throw std::runtime_error("Values are not equal " + msg);
    }
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
        assert_equal<std::string>("value_1_1", layer_1->get_value(key_1), "value_1_1");
        assert_equal<std::string>("value_1_2", layer_1->get_value(key_2), "value_1_2");
        assert_equal<std::string>("value_2_1", layer_2->get_value(key_1), "value_2_1");
        assert_equal<std::string>("value_2_2", layer_2->get_value(key_2), "value_2_2");
    });
}

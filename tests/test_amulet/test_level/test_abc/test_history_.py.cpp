#include <pybind11/pybind11.h>

#include <initializer_list>
#include <list>
#include <map>
#include <vector>

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
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2))
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_2_2", layer_2->get_value(key_2))

        ASSERT_EQUAL(size_t, 0, history_manager.get_undo_count())
        ASSERT_EQUAL(size_t, 0, history_manager.get_redo_count())

        // Create a new undo point.
        history_manager.create_undo_bin();

        ASSERT_EQUAL(size_t, 1, history_manager.get_undo_count())
        ASSERT_EQUAL(size_t, 0, history_manager.get_redo_count())

        // Overwrite values
        layer_1->set_value(key_2, "value_1_2b");
        layer_2->set_value(key_2, "value_2_2b");

        // Set new values
        TestResourceId key_3("key_3");
        layer_1->set_initial_value(key_3, "value_1_3");
        layer_2->set_initial_value(key_3, "value_2_3");

        // Validate
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2b", layer_1->get_value(key_2))
        ASSERT_EQUAL(std::string, "value_1_3", layer_1->get_value(key_3))
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_2_2b", layer_2->get_value(key_2))
        ASSERT_EQUAL(std::string, "value_2_3", layer_2->get_value(key_3))

        // Undo and validate
        history_manager.undo();
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2))
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_2_2", layer_2->get_value(key_2))

        ASSERT_EQUAL(size_t, 0, history_manager.get_undo_count())
        ASSERT_EQUAL(size_t, 1, history_manager.get_redo_count())

        // Redo and validate
        history_manager.redo();
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2b", layer_1->get_value(key_2))
        ASSERT_EQUAL(std::string, "value_1_3", layer_1->get_value(key_3))
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_2_2b", layer_2->get_value(key_2))
        ASSERT_EQUAL(std::string, "value_2_3", layer_2->get_value(key_3))

        ASSERT_EQUAL(size_t, 1, history_manager.get_undo_count())
        ASSERT_EQUAL(size_t, 0, history_manager.get_redo_count())

        // Validate changed
        ASSERT_EQUAL(bool, false, layer_1->get_resource(key_1).has_changed())
        ASSERT_EQUAL(bool, true, layer_1->get_resource(key_2).has_changed())
        ASSERT_EQUAL(bool, false, layer_1->get_resource(key_3).has_changed())
        ASSERT_EQUAL(bool, false, layer_2->get_resource(key_1).has_changed())
        ASSERT_EQUAL(bool, true, layer_2->get_resource(key_2).has_changed())
        ASSERT_EQUAL(bool, false, layer_2->get_resource(key_3).has_changed())

        // The owner would push the data to the level and call this to update the saved state.
        history_manager.mark_saved();

        // Validate changed
        ASSERT_EQUAL(bool, false, layer_1->get_resource(key_1).has_changed())
        ASSERT_EQUAL(bool, false, layer_1->get_resource(key_2).has_changed())
        ASSERT_EQUAL(bool, false, layer_1->get_resource(key_3).has_changed())
        ASSERT_EQUAL(bool, false, layer_2->get_resource(key_1).has_changed())
        ASSERT_EQUAL(bool, false, layer_2->get_resource(key_2).has_changed())
        ASSERT_EQUAL(bool, false, layer_2->get_resource(key_3).has_changed())

        // Undo
        history_manager.undo();
        // Validate changed
        ASSERT_EQUAL(bool, false, layer_1->get_resource(key_1).has_changed())
        ASSERT_EQUAL(bool, true, layer_1->get_resource(key_2).has_changed())
        ASSERT_EQUAL(bool, false, layer_1->get_resource(key_3).has_changed())
        ASSERT_EQUAL(bool, false, layer_2->get_resource(key_1).has_changed())
        ASSERT_EQUAL(bool, true, layer_2->get_resource(key_2).has_changed())
        ASSERT_EQUAL(bool, false, layer_2->get_resource(key_3).has_changed())

        // create a new undo point
        history_manager.create_undo_bin();

        ASSERT_EQUAL(size_t, 1, history_manager.get_undo_count())
        ASSERT_EQUAL(size_t, 0, history_manager.get_redo_count())

        // Validate
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2))
        ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_2_2", layer_2->get_value(key_2))

        // Test resetting
        history_manager.reset();
        ASSERT_EQUAL(size_t, 0, layer_1->get_resources().size())
        ASSERT_EQUAL(size_t, 0, layer_2->get_resources().size())

        layer_1->set_initial_value(key_1, "value_1_1");
        layer_1->set_initial_value(key_2, "value_1_2");
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2))

        // Test batch writing with initializer_list
        history_manager.create_undo_bin();
        std::initializer_list<std::pair<TestResourceId, std::string>> initializer_list_batch {
            { key_1, "value_1_1_initializer_list" },
            { key_2, "value_1_2_initializer_list" },
        };
        layer_1->set_values<std::initializer_list<std::pair<TestResourceId, std::string>>>(initializer_list_batch);

        ASSERT_EQUAL(std::string, "value_1_1_initializer_list", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_initializer_list", layer_1->get_value(key_2))

        // Test batch writing with list
        history_manager.create_undo_bin();
        std::list<std::pair<TestResourceId, std::string>> list_batch {
            { key_1, "value_1_1_list" },
            { key_2, "value_1_2_list" },
        };
        layer_1->set_values<std::list<std::pair<TestResourceId, std::string>>>(list_batch);

        ASSERT_EQUAL(std::string, "value_1_1_list", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_list", layer_1->get_value(key_2))

        // Test batch writing with vector
        history_manager.create_undo_bin();
        std::vector<std::pair<TestResourceId, std::string>> vector_batch {
            { key_1, "value_1_1_vector" },
            { key_2, "value_1_2_vector" },
        };
        layer_1->set_values<std::vector<std::pair<TestResourceId, std::string>>>(vector_batch);

        ASSERT_EQUAL(std::string, "value_1_1_vector", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_vector", layer_1->get_value(key_2))

        // Test batch writing with map
        history_manager.create_undo_bin();
        std::map<TestResourceId, std::string> map_batch {
            { key_1, "value_1_1_map" },
            { key_2, "value_1_2_map" },
        };
        layer_1->set_values<>(map_batch);

        ASSERT_EQUAL(std::string, "value_1_1_map", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_map", layer_1->get_value(key_2))

        history_manager.undo();
        ASSERT_EQUAL(std::string, "value_1_1_vector", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_vector", layer_1->get_value(key_2))

        history_manager.undo();
        ASSERT_EQUAL(std::string, "value_1_1_list", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_list", layer_1->get_value(key_2))

        history_manager.undo();
        ASSERT_EQUAL(std::string, "value_1_1_initializer_list", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_initializer_list", layer_1->get_value(key_2))

        history_manager.undo();
        ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2))

        history_manager.redo();
        ASSERT_EQUAL(std::string, "value_1_1_initializer_list", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_initializer_list", layer_1->get_value(key_2))

        history_manager.redo();
        ASSERT_EQUAL(std::string, "value_1_1_list", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_list", layer_1->get_value(key_2))

        history_manager.redo();
        ASSERT_EQUAL(std::string, "value_1_1_vector", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_vector", layer_1->get_value(key_2))

        history_manager.redo();
        ASSERT_EQUAL(std::string, "value_1_1_map", layer_1->get_value(key_1))
        ASSERT_EQUAL(std::string, "value_1_2_map", layer_1->get_value(key_2))
    });
}

#include <pybind11/pybind11.h>

#include <initializer_list>
#include <list>
#include <map>
#include <string>
#include <type_traits>
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

template <typename T>
std::string cast_to_string(const T& obj)
{
    if constexpr (std::is_arithmetic_v<T>) {
        return std::to_string(obj);
    } else if constexpr (std::is_same_v<T, std::string> || std::is_convertible_v<T, std::string>) {
        return obj;
    } else {
        return "";
    }
}

#define ASSERT_EQUAL(CLS, A, B)                        \
    {                                                  \
        CLS a;                                         \
        try {                                          \
            a = A;                                     \
        } catch (const std::exception& e) {            \
            std::string msg;                           \
            msg.reserve(200);                          \
            msg += "Failed evaluating A in file ";     \
            msg += __FILE__;                           \
            msg += " at line ";                        \
            msg += std::to_string(__LINE__);           \
            msg += ". ";                               \
            msg += e.what();                           \
            throw std::runtime_error(msg);             \
        }                                              \
        CLS b;                                         \
        try {                                          \
            b = B;                                     \
        } catch (const std::exception& e) {            \
            std::string msg;                           \
            msg.reserve(200);                          \
            msg += "Failed evaluating B in file ";     \
            msg += __FILE__;                           \
            msg += " at line ";                        \
            msg += std::to_string(__LINE__);           \
            msg += ". ";                               \
            msg += e.what();                           \
            throw std::runtime_error(msg);             \
        }                                              \
        if (a != b) {                                  \
            std::string msg;                           \
            msg.reserve(200);                          \
            msg += "Values are not equal in file ";    \
            msg += __FILE__;                           \
            msg += " at line ";                        \
            msg += std::to_string(__LINE__);           \
            msg += ".";                                \
            auto a_msg = cast_to_string(a);            \
            if (!a_msg.empty()) {                      \
                msg += " Expected \"" + a_msg + "\"."; \
            }                                          \
            auto b_msg = cast_to_string(b);            \
            if (!a_msg.empty()) {                      \
                msg += " Got \"" + b_msg + "\".";      \
            }                                          \
            throw std::runtime_error(msg);             \
        }                                              \
    }

#define ASSERT_RAISES(EXC, A)                         \
    {                                                 \
        bool err_raised = false;                      \
        try {                                         \
            A;                                        \
        } catch (const EXC&) {                        \
            err_raised = true;                        \
        } catch (...) {                               \
            std::string msg;                          \
            msg.reserve(200);                         \
            msg += "Other exception raised in file "; \
            msg += __FILE__;                          \
            msg += " at line ";                       \
            msg += std::to_string(__LINE__);          \
            msg += ". ";                              \
            throw std::runtime_error(msg);            \
        }                                             \
        if (!err_raised) {                            \
            std::string msg;                          \
            msg.reserve(200);                         \
            msg += "Exception not raised in file ";   \
            msg += __FILE__;                          \
            msg += " at line ";                       \
            msg += std::to_string(__LINE__);          \
            msg += ". ";                              \
            throw std::runtime_error(msg);            \
        }                                             \
    }

static void test_history()
{
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
    ASSERT_EQUAL(size_t, 0, history_manager.get_undo_count())
    ASSERT_EQUAL(size_t, 1, history_manager.get_redo_count())
    ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2))
    ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_2_2", layer_2->get_value(key_2))

    // Redo and validate
    history_manager.redo();
    ASSERT_EQUAL(size_t, 1, history_manager.get_undo_count())
    ASSERT_EQUAL(size_t, 0, history_manager.get_redo_count())
    ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_1_2b", layer_1->get_value(key_2))
    ASSERT_EQUAL(std::string, "value_1_3", layer_1->get_value(key_3))
    ASSERT_EQUAL(std::string, "value_2_1", layer_2->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_2_2b", layer_2->get_value(key_2))
    ASSERT_EQUAL(std::string, "value_2_3", layer_2->get_value(key_3))

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
    layer_1->set_values(initializer_list_batch);

    ASSERT_EQUAL(std::string, "value_1_1_initializer_list", layer_1->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_1_2_initializer_list", layer_1->get_value(key_2))

    // Test batch writing with list
    history_manager.create_undo_bin();
    std::list<std::pair<TestResourceId, std::string>> list_batch {
        { key_1, "value_1_1_list" },
        { key_2, "value_1_2_list" },
    };
    layer_1->set_values(list_batch);

    ASSERT_EQUAL(std::string, "value_1_1_list", layer_1->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_1_2_list", layer_1->get_value(key_2))

    // Test batch writing with vector
    history_manager.create_undo_bin();
    std::vector<std::pair<TestResourceId, std::string>> vector_batch {
        { key_1, "value_1_1_vector" },
        { key_2, "value_1_2_vector" },
    };
    layer_1->set_values(vector_batch);

    ASSERT_EQUAL(std::string, "value_1_1_vector", layer_1->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_1_2_vector", layer_1->get_value(key_2))

    // Test batch writing with map
    history_manager.create_undo_bin();
    std::map<TestResourceId, std::string> map_batch {
        { key_1, "value_1_1_map" },
        { key_2, "value_1_2_map" },
    };
    layer_1->set_values(map_batch);

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

    // Test for ghosts
    history_manager.reset();
    layer_1->set_initial_value(key_1, "value_1_1");
    history_manager.create_undo_bin();
    ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))

    // Test default values
    history_manager.reset();
    layer_1->set_initial_value(key_1, "value_1_1");
    // Second undo point
    history_manager.create_undo_bin();
    layer_1->set_value(key_1, "value_1_1b");
    layer_1->set_initial_value(key_2, "value_1_2");
    layer_1->set_value(key_2, "value_1_2b");
    // Validate
    ASSERT_EQUAL(std::string, "value_1_1b", layer_1->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_1_2b", layer_1->get_value(key_2))
    history_manager.undo();
    ASSERT_EQUAL(std::string, "value_1_1", layer_1->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_1_2", layer_1->get_value(key_2))
    history_manager.redo();
    ASSERT_EQUAL(std::string, "value_1_1b", layer_1->get_value(key_1))
    ASSERT_EQUAL(std::string, "value_1_2b", layer_1->get_value(key_2))
}

static void test_undo_overwrite()
{
    // Create the history manager.
    Amulet::HistoryManager history_manager;
    auto layer_1 = history_manager.new_layer<std::string>();

    // Set the initial value
    layer_1->set_initial_value("key", "val0");
    ASSERT_EQUAL(std::string, "val0", layer_1->get_value("key"))

    // Set new state
    history_manager.create_undo_bin();
    layer_1->set_value("key", "val1");
    ASSERT_EQUAL(std::string, "val1", layer_1->get_value("key"))

    // Set another new state
    history_manager.create_undo_bin();
    layer_1->set_value("key", "val2");
    ASSERT_EQUAL(std::string, "val2", layer_1->get_value("key"))

    // undo and overwrite the second state
    history_manager.undo();
    layer_1->set_value("key", "val3");
    ASSERT_EQUAL(std::string, "val3", layer_1->get_value("key"))

    // Read the original state
    history_manager.undo();
    ASSERT_EQUAL(std::string, "val0", layer_1->get_value("key"))
}

static void test_set_value_enum()
{
    // Create the history manager.
    Amulet::HistoryManager history_manager;
    auto layer = history_manager.new_layer<std::string>();

    history_manager.create_undo_bin();
    layer->set_initial_value("default_false", "default_false_val");
    layer->set_initial_value("error_false", "error_false_val");
    layer->set_initial_value("empty_false", "empty_false_val");
    layer->set_initial_value("value_false", "value_false_val");

    // Set default
    layer->set_value("default_false", "default_false_val_2");
    ASSERT_RAISES(std::runtime_error, layer->set_value("default_true", "default_true_val"))

    // Set Error
    layer->set_value<Amulet::HistoryInitialisationMode::Error>("error_false", "error_false_val_2");
    ASSERT_RAISES(std::runtime_error, layer->set_value<Amulet::HistoryInitialisationMode::Error>("error_true", "error_true_val"))

    // Set Empty
    layer->set_value<Amulet::HistoryInitialisationMode::Empty>("empty_false", "empty_false_val_2");
    layer->set_value<Amulet::HistoryInitialisationMode::Empty>("empty_true", "empty_true_val");

    // Set Value
    layer->set_value<Amulet::HistoryInitialisationMode::Value>("value_false", "value_false_val_2");
    layer->set_value<Amulet::HistoryInitialisationMode::Value>("value_true", "value_true_val");

    // Validate default
    ASSERT_EQUAL(std::string, "default_false_val_2", layer->get_value("default_false"))
    ASSERT_RAISES(std::out_of_range, layer->get_value("default_true"))

    // Validate Error
    ASSERT_EQUAL(std::string, "error_false_val_2", layer->get_value("error_false"))
    ASSERT_RAISES(std::out_of_range, layer->get_value("error_true"))

    // Validate Empty
    ASSERT_EQUAL(std::string, "empty_false_val_2", layer->get_value("empty_false"))
    ASSERT_EQUAL(std::string, "empty_true_val", layer->get_value("empty_true"))

    // Validate Value
    ASSERT_EQUAL(std::string, "value_false_val_2", layer->get_value("value_false"))
    ASSERT_EQUAL(std::string, "value_true_val", layer->get_value("value_true"))

    // Undo and validate original values
    history_manager.undo();

    // Validate default
    ASSERT_EQUAL(std::string, "default_false_val", layer->get_value("default_false"))
    ASSERT_RAISES(std::out_of_range, layer->get_value("default_true"))

    // Validate Error
    ASSERT_EQUAL(std::string, "error_false_val", layer->get_value("error_false"))
    ASSERT_RAISES(std::out_of_range, layer->get_value("error_true"))

    // Validate Empty
    ASSERT_EQUAL(std::string, "empty_false_val", layer->get_value("empty_false"))
    ASSERT_EQUAL(std::string, "", layer->get_value("empty_true"))

    // Validate Value
    ASSERT_EQUAL(std::string, "value_false_val", layer->get_value("value_false"))
    ASSERT_EQUAL(std::string, "value_true_val", layer->get_value("value_true"))
}

static void test_set_values_enum()
{
    // Create the history manager.
    Amulet::HistoryManager history_manager;
    auto layer = history_manager.new_layer<std::string>();

    history_manager.create_undo_bin();
    layer->set_initial_value("default_false_1", "default_false_1_val");
    layer->set_initial_value("default_false_2", "default_false_2_val");
    layer->set_initial_value("error_false_1", "error_false_1_val");
    layer->set_initial_value("error_false_2", "error_false_2_val");
    layer->set_initial_value("empty_false", "empty_false_val");
    layer->set_initial_value("value_false", "value_false_val");

    // Set default - all exist
    layer->set_values({ std::make_pair("default_false_1", "default_false_1_val_2"), std::make_pair("default_false_2", "default_false_2_val_2") });
    ASSERT_EQUAL(std::string, "default_false_1_val_2", layer->get_value("default_false_1"))
    ASSERT_EQUAL(std::string, "default_false_2_val_2", layer->get_value("default_false_2"))
    // Set default - half exist
    ASSERT_RAISES(std::runtime_error, layer->set_values({ std::make_pair("default_false_1", "default_false_1_val_3"), std::make_pair("default_true", "default_true_val") }))
    ASSERT_EQUAL(std::string, "default_false_1_val_2", layer->get_value("default_false_1"))
    ASSERT_EQUAL(std::string, "default_false_2_val_2", layer->get_value("default_false_2"))
    ASSERT_RAISES(std::out_of_range, layer->get_value("default_true"))

    // Set Error - all exist
    layer->set_values<Amulet::HistoryInitialisationMode::Error>({ std::make_pair("error_false_1", "error_false_1_val_2"), std::make_pair("error_false_2", "error_false_2_val_2") });
    ASSERT_EQUAL(std::string, "error_false_1_val_2", layer->get_value("error_false_1"))
    ASSERT_EQUAL(std::string, "error_false_2_val_2", layer->get_value("error_false_2"))
    // Set Error - half exist
    ASSERT_RAISES(std::runtime_error, layer->set_values<Amulet::HistoryInitialisationMode::Error>({ std::make_pair("error_false_1", "error_false_1_val_3"), std::make_pair("error_true", "error_true_val") }))
    ASSERT_EQUAL(std::string, "error_false_1_val_2", layer->get_value("error_false_1"))
    ASSERT_EQUAL(std::string, "error_false_2_val_2", layer->get_value("error_false_2"))
    ASSERT_RAISES(std::out_of_range, layer->get_value("error_true"))

    // Set Empty - half exist
    layer->set_values<Amulet::HistoryInitialisationMode::Empty>({ std::make_pair("empty_false", "empty_false_val_2"), std::make_pair("empty_true", "empty_true_val") });
    ASSERT_EQUAL(std::string, "empty_false_val_2", layer->get_value("empty_false"))
    ASSERT_EQUAL(std::string, "empty_true_val", layer->get_value("empty_true"))

    // Set Value - half exist
    layer->set_values<Amulet::HistoryInitialisationMode::Value>({ std::make_pair("value_false", "value_false_val_2"), std::make_pair("value_true", "value_true_val") });
    ASSERT_EQUAL(std::string, "value_false_val_2", layer->get_value("value_false"))
    ASSERT_EQUAL(std::string, "value_true_val", layer->get_value("value_true"))

    // Undo and validate original values
    history_manager.undo();

    // Validate default
    ASSERT_EQUAL(std::string, "default_false_1_val", layer->get_value("default_false_1"))
    ASSERT_EQUAL(std::string, "default_false_2_val", layer->get_value("default_false_2"))
    ASSERT_RAISES(std::out_of_range, layer->get_value("default_true"))

    // Validate Error
    ASSERT_EQUAL(std::string, "error_false_1_val", layer->get_value("error_false_1"))
    ASSERT_EQUAL(std::string, "error_false_2_val", layer->get_value("error_false_2"))
    ASSERT_RAISES(std::out_of_range, layer->get_value("error_true"))

    // Validate Empty
    ASSERT_EQUAL(std::string, "empty_false_val", layer->get_value("empty_false"))
    ASSERT_EQUAL(std::string, "", layer->get_value("empty_true"))

    // Validate Value
    ASSERT_EQUAL(std::string, "value_false_val", layer->get_value("value_false"))
    ASSERT_EQUAL(std::string, "value_true_val", layer->get_value("value_true"))
}

void init_test_history(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_history_");
    m.def("test_history", &test_history);
    m.def("test_undo_overwrite", &test_undo_overwrite);
    m.def("test_set_value_enum", &test_set_value_enum);
    m.def("test_set_values_enum", &test_set_values_enum);
}

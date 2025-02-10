#include <pybind11/pybind11.h>

#include <string>

#include <amulet/utils/signal.hpp>
#include <amulet/utils/signal.py.hpp>

namespace py = pybind11;

namespace AmuletTest {

class SignalTest {
public:
    Amulet::Signal<> signal_0;
    Amulet::Signal<int> signal_1;
    Amulet::Signal<int, float> signal_2;
    Amulet::Signal<int, float, std::string> signal_3;

    void emit()
    {
        signal_0.emit();
        signal_1.emit(1);
        signal_2.emit(1, 1.5);
        signal_3.emit(1, 1.5, "Hello World");
    }
};

} // namespace AmuletTest

void init_test_signal(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_signal_");

    py::class_<AmuletTest::SignalTest> SignalTest(m, "SignalTest");
    SignalTest.def(py::init<>());
    SignalTest.def_property_readonly("signal_0", [](AmuletTest::SignalTest& self) { return Amulet::make_signal(self.signal_0); });
    SignalTest.def_property_readonly("signal_1", [](AmuletTest::SignalTest& self) { return Amulet::make_signal(self.signal_1); });
    SignalTest.def_property_readonly("signal_2", [](AmuletTest::SignalTest& self) { return Amulet::make_signal(self.signal_2); });
    SignalTest.def_property_readonly("signal_3", [](AmuletTest::SignalTest& self) { return Amulet::make_signal(self.signal_3); });
    SignalTest.def("emit", &AmuletTest::SignalTest::emit);
}

#include "abc.hpp"
#include <amuletcpp/version.hpp>


namespace py = pybind11;

PYBIND11_MODULE(version, m) {
    py::options options;

    py::object ABC = py::module_::import("amulet.abc").attr("ABC");
    m.attr("PlatformType") = py::module_::import("builtins").attr("str");

    py::class_<Amulet::VersionNumber, std::shared_ptr<Amulet::VersionNumber>> VersionNumber(m, "VersionNumber", ABC,
R"doc(This class is designed to store semantic versions and data versions and allow comparisons between them.

>>> v1 = VersionNumber(1, 0, 0)
>>> v2 = VersionNumber(1, 0)
>>> assert v2 == v1

This class should also be used to store single number data versions.
>>> v3 = VersionNumber(3578)
)doc");

        options.disable_function_signatures();
        VersionNumber.def(
            py::init(
            [](py::args v){return std::make_shared<Amulet::VersionNumber>(v.cast<std::vector<std::int64_t>>());}),
            py::doc("__init__(self: amulet.version.VersionNumber, *args: typing.SupportsInt) -> None"));

        // Start collections.abc.Sequence
        VersionNumber.def(
            "__getitem__",
            &Amulet::VersionNumber::operator[],
            py::doc(
R"doc(__getitem__(*args, **kwargs)
Overloaded function.
1. __getitem__(self: amulet.version.VersionNumber, item: typing.SupportsInt) -> int
2. __getitem__(self: amulet.version.VersionNumber, item: slice) -> list[int]
)doc"));
        VersionNumber.def(
            "__getitem__",
            [](const Amulet::VersionNumber& self, const py::slice &slice) -> std::vector<std::int64_t> {
                size_t start = 0, stop = 0, step = 0, slicelength = 0;
                if (!slice.compute(self.size(), &start, &stop, &step, &slicelength)) {
                    throw py::error_already_set();
                }
                std::vector<std::int64_t> out(slicelength);
                for (size_t i = 0; i < slicelength; ++i) {
                    out[i] = self[start];
                    start += step;
                }
                return out;
            });
        options.enable_function_signatures();

        VersionNumber.def(
            "__len__",
            &Amulet::VersionNumber::size);

        VersionNumber.def(
            "__contains__",
            [](const Amulet::VersionNumber& self, std::int64_t value) {
                for (auto it = self.begin(); it != self.end(); it++){
                    if (*it == value) return true;
                }
                return false;
            });

        VersionNumber.def(
            "__iter__",
            [](const Amulet::VersionNumber& self) {return py::make_iterator(self.begin(), self.end());},
            py::keep_alive<0, 1>() /* Essential: keep object alive while iterator exists */);

        VersionNumber.def(
            "__reversed__",
            [](const Amulet::VersionNumber& self) {return py::make_iterator(self.rbegin(), self.rend());},
            py::keep_alive<0, 1>() /* Essential: keep object alive while iterator exists */);

        VersionNumber.def(
            "index",
            [](const Amulet::VersionNumber& self, std::int64_t value, size_t start, size_t stop) {
                start = std::min(start, self.size());
                stop = std::min(stop, self.size());
                for (size_t i = start; i < stop; i++){
                    if (self[i] == value) return i;
                }
                throw py::value_error(std::to_string(value) + " is not in VersionNumber.");
            },
            py::arg("value"), py::arg("start") = 0, py::arg("stop") = std::numeric_limits<size_t>::max());

        VersionNumber.def(
            "count",
            [](const Amulet::VersionNumber& self, std::int64_t value) {
                size_t count = 0;
                for (size_t i = 0; i < self.size(); i++){
                    if (self[i] == value) ++count;
                }
                return count;
            },
            py::arg("value"));

        // End collections.abc.Sequence

        VersionNumber.def(
            "__str__",
            &Amulet::VersionNumber::toString);

        VersionNumber.def(pybind11::self == pybind11::self);
        VersionNumber.def(pybind11::self != pybind11::self);
        VersionNumber.def(pybind11::self < pybind11::self);
        VersionNumber.def(pybind11::self > pybind11::self);
        VersionNumber.def(pybind11::self <= pybind11::self);
        VersionNumber.def(pybind11::self >= pybind11::self);

        VersionNumber.def(
            "cropped_version",
            [](const Amulet::VersionNumber& self) -> py::tuple {return py::cast(self.cropped_version());},
            py::doc("The version number with trailing zeros cut off."));

        VersionNumber.def(
            "padded_version",
            [](const Amulet::VersionNumber& self, size_t len) -> py::tuple {return py::cast(self.padded_version(len));},
            py::doc("Get the version number padded with zeros to the given length."),
            py::arg("len"));

        VersionNumber.def(
            "__hash__",
            [](const Amulet::VersionNumber& self) {
                py::tuple py_tuple = py::cast(self.cropped_version());
                return py::hash(py_tuple);
            });

    py::module_::import("collections.abc").attr("Sequence").attr("register")(VersionNumber);


    py::class_<Amulet::PlatformVersionContainer, std::shared_ptr<Amulet::PlatformVersionContainer>> PlatformVersionContainer(m, "PlatformVersionContainer", ABC);
        PlatformVersionContainer.def(
            py::init<const Amulet::PlatformType&, const Amulet::VersionNumber&>(),
            py::arg("platform"), py::arg("version"));
        PlatformVersionContainer.def_readonly("platform", &Amulet::PlatformVersionContainer::platform);
        PlatformVersionContainer.def_readonly("version", &Amulet::PlatformVersionContainer::version);

    py::class_<Amulet::VersionRange, std::shared_ptr<Amulet::VersionRange>> VersionRange(m, "VersionRange", ABC);
        VersionRange.def(
            py::init<const Amulet::PlatformType&, const Amulet::VersionNumber&, const Amulet::VersionNumber&>(),
            py::arg("platform"), py::arg("min_version"), py::arg("max_version"));
        VersionRange.def_readonly("platform", &Amulet::VersionRange::platform);
        VersionRange.def_readonly("min_version", &Amulet::VersionRange::min_version);
        VersionRange.def_readonly("max_version", &Amulet::VersionRange::max_version);
        VersionRange.def(
            "contains",
            &Amulet::VersionRange::contains);

    py::class_<Amulet::VersionRangeContainer, std::shared_ptr<Amulet::VersionRangeContainer>> VersionRangeContainer(m, "VersionRangeContainer", ABC);
        VersionRangeContainer.def(
            py::init<const Amulet::VersionRange&>(),
            py::arg("version_range"));
        VersionRangeContainer.def_readonly("version_range", &Amulet::VersionRangeContainer::version_range);
}

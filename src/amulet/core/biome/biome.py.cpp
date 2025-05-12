#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include <amulet/pybind11_extensions/py_module.hpp>

#include <memory>
#include <span>

#include "biome.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_biome(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "biome");
    py::class_<Amulet::Biome, Amulet::PlatformVersionContainer, std::shared_ptr<Amulet::Biome>> Biome(m, "Biome",
        "A class to manage the state of a biome.\n"
        "\n"
        "It is an immutable object that contains the platform, version, namespace and base name.\n"
        "\n"
        "Here's a few examples on how create a Biome object:\n"
        "\n"
        ">>> # Create a plains biome for Java 1.20.2\n"
        ">>> plains = Biome(\"java\", VersionNumber(3578), \"minecraft\", \"plains\")\n"
        ">>> # The version number for Java is the Java data version\n"
        "\n"
        ">>> # Create a plains biome for Bedrock \n"
        ">>> plains = Biome(\"bedrock\", VersionNumber(1, 21, 0, 3), \"minecraft\", \"plains\")\n"
        ">>> # The biome version number is unused in Bedrock but it is here for completeness.");
    Biome.def(
        py::init<
            const Amulet::PlatformType&,
            const Amulet::VersionNumber&,
            const std::string&,
            const std::string&>(),
        py::arg("platform"),
        py::arg("version"),
        py::arg("namespace"),
        py::arg("base_name"));
    Biome.def_property_readonly(
        "namespaced_name",
        [](const Amulet::Biome& self) {
            return self.get_namespace() + ":" + self.get_base_name();
        },
        py::doc(
            "The namespaced id of the :class:`Biome` object.\n"
            "\n"
            ">>> biome: Biome\n"
            ">>> biome.namespaced_name\n"
            "\n"
            ":return: The \"namespace:base_name\" of the biome"));
    Biome.def_property_readonly(
        "namespace",
        &Amulet::Biome::get_namespace,
        py::doc(
            "The namespace of the :class:`Biome` object.\n"
            "\n"
            ">>> biome: Biome\n"
            ">>> water.namespace\n"
            "\n"
            ":return: The namespace of the biome"));
    Biome.def_property_readonly(
        "base_name",
        &Amulet::Biome::get_base_name,
        py::doc(
            "The base name of the :class:`Biome` object.\n"
            "\n"
            ">>> biome: Biome\n"
            ">>> biome.base_name\n"
            "\n"
            ":return: The base name of the biome"));
    Biome.def(
        "__repr__",
        [](const Amulet::Biome& self) {
            return "Biome("
                + py::repr(py::cast(self.get_platform())).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_version(), py::return_value_policy::reference)).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_namespace())).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_base_name())).cast<std::string>() + ")";
        });
    Biome.def(
        "__hash__",
        [](const Amulet::Biome& self) {
            return py::hash(
                py::make_tuple(
                    py::cast(self.get_platform()),
                    py::cast(self.get_version(), py::return_value_policy::reference),
                    py::cast(self.get_namespace()),
                    py::cast(self.get_base_name())));
        });
    Biome.def(
        py::pickle(
            [](const Amulet::Biome& self) -> py::bytes {
                return py::bytes(Amulet::serialise(self));
            },
            [](py::bytes state) {
                return Amulet::deserialise<Amulet::Biome>(state.cast<std::string>());
            }));

    Biome.def(py::self == py::self);
    Biome.def(py::self > py::self);
    Biome.def(py::self < py::self);
    Biome.def(py::self >= py::self);
    Biome.def(py::self <= py::self);
}

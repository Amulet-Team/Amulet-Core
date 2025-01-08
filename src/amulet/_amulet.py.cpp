#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>
namespace py = pybind11;

void init_collections(py::module);
void init_utils(py::module);
void init_version(py::module);
void init_selection(py::module);
void init_block(py::module);
void init_block_entity(py::module);
void init_biome(py::module);
void init_palette(py::module);
void init_chunk(py::module);
void init_chunk_components(py::module);
void init_level(py::module);
void init_block_mesh(py::module);

static std::string get_version_top(std::string version){
    return version.substr(0, version.find('.', version.find('.') + 1));
}

static void check_compatibility(py::module a, std::string a_name, py::module b, std::string b_name){
    py::dict a_config = a.attr("compiler_config");
    py::dict b_config = b.attr("compiler_config");

    std::string a_pybind11_version = a_config["pybind11_version"].cast<std::string>();
    std::string b_pybind11_version = b_config["pybind11_version"].cast<std::string>();
    if (a_pybind11_version != b_pybind11_version){
        throw std::runtime_error(
            "pybind11 version mismatch. " +
            a_name + " is compiled for pybind11==" + a_pybind11_version +
            " and " +
            b_name + " is compiled for pybind11==" + b_pybind11_version
        );
    }

    std::string a_compiler_id = a_config["compiler_id"].cast<std::string>();
    std::string b_compiler_id = b_config["compiler_id"].cast<std::string>();
    if (a_compiler_id != b_compiler_id){
        throw std::runtime_error(
            "compiler mismatch. " +
            a_name + " is compiled by " + a_compiler_id +
            " and " +
            b_name + " is compiled by " + b_compiler_id
        );
    }

    std::string a_compiler_version = a_config["compiler_version"].cast<std::string>();
    std::string b_compiler_version = b_config["compiler_version"].cast<std::string>();
    if (get_version_top(a_compiler_version) != get_version_top(b_compiler_version)){
        throw std::runtime_error(
            "compiler version mismatch. " +
            a_name + " is compiled by " + a_compiler_id + " " + a_compiler_version +
            " and " +
            b_name + " is compiled by " + b_compiler_id + " " + b_compiler_version
        );
    }
}

void init_module(py::module m){
    auto amulet_nbt = py::module::import("amulet_nbt");
    auto leveldb = py::module::import("leveldb");

    py::dict compiler_config;
    compiler_config["pybind11_version"] = PYBIND11_VERSION;
    compiler_config["compiler_id"] = COMPILER_ID;
    compiler_config["compiler_version"] = COMPILER_VERSION;
    m.attr("compiler_config") = compiler_config;

    check_compatibility(amulet_nbt, "amulet_nbt", m, "amulet");
    check_compatibility(leveldb, "leveldb", m, "amulet");

    // Submodules
    init_collections(m);
    init_utils(m);
    init_version(m);
    init_selection(m);
    init_block(m);
    init_block_entity(m);
    init_biome(m);
    init_palette(m);
    init_chunk(m);
    init_chunk_components(m);
    init_level(m);
    init_block_mesh(m);
}

PYBIND11_MODULE(_amulet, m) {
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}

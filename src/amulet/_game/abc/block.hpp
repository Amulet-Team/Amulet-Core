#pragma once

#include <variant>
#include <optional>
#include <memory>

#include <pybind11/pybind11.h>

#include <amulet/block.hpp>
#include <amulet/block_entity.hpp>
#include <amulet/entity.hpp>

namespace py = pybind11;

namespace Amulet {

class BlockData {
protected:
    std::unique_ptr<py::object> _block_data;

public:
    BlockData(py::object);
    ~BlockData();

    std::variant<
        std::tuple<Block, std::optional<BlockEntity>, bool>,
        std::tuple<Entity, bool>>
    translate(const std::string& platform, const VersionNumber& version, const Block& block);
};

} // namespace Amulet

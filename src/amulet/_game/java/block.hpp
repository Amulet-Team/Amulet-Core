#pragma once

#include <amulet/_game/abc/block.hpp>

namespace Amulet {

enum class Waterloggable {
    No, // Cannot be waterlogged.
    Yes, // Can be waterlogged.
    Always // Is always waterlogged. (attribute is not stored)
};

class JavaBlockData : public BlockData {
public:
    using BlockData::BlockData;

    Waterloggable is_waterloggable(const std::string& namespace_, const std::string& base_name);
};

} // namespace Amulet

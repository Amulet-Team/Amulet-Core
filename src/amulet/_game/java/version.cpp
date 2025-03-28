#include "version.hpp"

namespace Amulet {

std::shared_ptr<JavaBlockData> JavaGameVersion::get_block_data()
{
    py::gil_scoped_acquire gil;
    return std::make_shared<JavaBlockData>(_game_version.attr("block"));
}

} // namespace Amulet

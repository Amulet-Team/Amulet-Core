#include "block.hpp"

namespace Amulet {

Waterloggable JavaBlockData::is_waterloggable(const std::string& namespace_, const std::string& base_name)
{
    py::gil_scoped_acquire gil;
    return _block_data->attr("waterloggable")(namespace_, base_name).cast<Waterloggable>();
}

} // namespace Amulet

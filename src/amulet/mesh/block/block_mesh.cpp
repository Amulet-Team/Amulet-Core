#include <string>
#include <array>
#include "block_mesh.hpp"

namespace Amulet {

const std::array<CullDirection, 4> roty_map = { CullNorth, CullEast, CullSouth, CullWest };

const RotationCullMapType RotationCullMap = []() {
    RotationCullMapType cull_map;
    for (std::int8_t roty = -3; roty < 4; roty++) {
        // Create the rotated Y array
        std::array<CullDirection, 4> roty_map_rotated;
        auto split_y_point = 0 <= roty ? roty : roty + roty_map.size();
        std::copy(roty_map.begin() + split_y_point, roty_map.end(), roty_map_rotated.begin());
        std::copy(roty_map.begin(), roty_map.begin() + split_y_point, roty_map_rotated.end() - split_y_point);
        // Create the X array
        const std::array<CullDirection, 4> rotx_map = { roty_map_rotated[0], CullDown, roty_map_rotated[2], CullUp };
        
        for (std::int8_t rotx = -3; rotx < 4; rotx++) { 
            // Create the rotated X array
            std::array<CullDirection, 4> rotx_map_rotated;
            auto split_x_point = 0 <= rotx ? rotx : rotx + rotx_map.size();
            std::copy(rotx_map.begin() + split_x_point, rotx_map.end(), rotx_map_rotated.begin());
            std::copy(rotx_map.begin(), rotx_map.begin() + split_x_point, rotx_map_rotated.end() - split_x_point);

            cull_map[std::make_pair(roty, rotx)] = {
                CullNone,
                rotx_map_rotated[3],
                rotx_map_rotated[1],
                rotx_map_rotated[0],
                roty_map_rotated[1],
                rotx_map_rotated[2],
                roty_map_rotated[3]
            };
        }
    }
    return cull_map;
}();

BlockMesh merge_block_mesh(std::initializer_list<std::reference_wrapper<BlockMesh>> meshes) {
    BlockMesh new_mesh;
    return new_mesh;
}

}

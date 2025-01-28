#include <array>
#include <functional>
#include <string>

#include "block_mesh.hpp"
#include <amulet/dll.hpp>

namespace Amulet {

const std::array<BlockMeshCullDirection, 4> roty_map = { BlockMeshCullNorth, BlockMeshCullEast, BlockMeshCullSouth, BlockMeshCullWest };

// For every combination of 90 degree rotations in y and x axis
// gives the rotated cull direction.
const RotationCullMapType RotationCullMap = []() {
    RotationCullMapType cull_map;
    for (std::int8_t roty = -3; roty < 4; roty++) {
        // Create the rotated Y array
        std::array<BlockMeshCullDirection, 4> roty_map_rotated;
        auto split_y_point = 0 <= roty ? roty : roty + roty_map.size();
        std::copy(roty_map.begin() + split_y_point, roty_map.end(), roty_map_rotated.begin());
        std::copy(roty_map.begin(), roty_map.begin() + split_y_point, roty_map_rotated.end() - split_y_point);
        // Create the X array
        const std::array<BlockMeshCullDirection, 4> rotx_map = { roty_map_rotated[0], BlockMeshCullDown, roty_map_rotated[2], BlockMeshCullUp };

        for (std::int8_t rotx = -3; rotx < 4; rotx++) {
            // Create the rotated X array
            std::array<BlockMeshCullDirection, 4> rotx_map_rotated;
            auto split_x_point = 0 <= rotx ? rotx : rotx + rotx_map.size();
            std::copy(rotx_map.begin() + split_x_point, rotx_map.end(), rotx_map_rotated.begin());
            std::copy(rotx_map.begin(), rotx_map.begin() + split_x_point, rotx_map_rotated.end() - split_x_point);

            cull_map[std::make_pair(roty, rotx)] = {
                BlockMeshCullNone,
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

BlockMesh BlockMesh::rotate(std::int8_t rotx, std::int8_t roty) const
{
    if (rotx || roty) {
        auto rotation_key = std::make_pair(rotx, roty);
        auto it = RotationCullMap.find(rotation_key);
        if (it != RotationCullMap.end()) {
            const auto& cull_map = it->second;
            BlockMesh mesh;
            mesh.transparency = transparency;
            mesh.textures = textures;

            // Compuate rotation values
            float theta_x = static_cast<float>(std::numbers::pi * rotx / 2.0);
            float theta_y = static_cast<float>(std::numbers::pi * roty / 2.0);
            float sin_x = std::sin(theta_x);
            float cos_x = std::cos(theta_x);
            float sin_y = std::sin(theta_y);
            float cos_y = std::cos(theta_y);

            for (std::uint8_t cull_direction = 0; cull_direction < 7; cull_direction++) {
                // Copy the part to the new cull direction.
                auto new_cull_direction = cull_map[cull_direction];
                auto& part = mesh.parts[new_cull_direction] = parts[cull_direction];

                if (part) {
                    // Rotate the vertex coords.
                    for (auto& vertex : part->verts) {
                        auto& coord = vertex.coord;
                        float x = coord.x - 0.5f;
                        float y = coord.y - 0.5f;
                        float z = coord.z - 0.5f;

                        // Rotate in X axis
                        float y_ = y * cos_x - z * sin_x;
                        z = y * sin_x + z * cos_x;
                        y = y_;

                        // Rotate in Y axis
                        float x_ = x * cos_y + z * sin_y;
                        z = -x * sin_y + z * cos_y;
                        x = x_;

                        coord.x = x + 0.5f;
                        coord.y = y + 0.5f;
                        coord.z = z + 0.5f;
                    }
                }
            }
            return mesh;
        }
    }
    return *this;
}

BlockMesh merge_block_meshes(std::vector<std::reference_wrapper<const BlockMesh>> meshes)
{
    BlockMesh new_mesh;
    new_mesh.transparency = BlockMeshTransparency::Partial;
    std::map<std::string, size_t> texture_index_map;
    for (const auto& wrapper : meshes) {
        const auto& temp_mesh = wrapper.get();
        // Get the minimum transparency of the two meshes.
        new_mesh.transparency = std::min(new_mesh.transparency, temp_mesh.transparency);

        // Copy over mesh parts
        for (std::uint8_t cull_direction = 0; cull_direction < 7; cull_direction++) {
            const auto& temp_mesh_part = temp_mesh.parts[cull_direction];
            if (temp_mesh_part) {
                auto& new_mesh_part = new_mesh.parts[cull_direction];
                if (!new_mesh_part) {
                    // Initialise the mesh part if it is null.
                    new_mesh_part = BlockMeshPart();
                }
                // Get the number of triangles before copying
                size_t vert_count = new_mesh_part->verts.size();
                size_t triangle_count = new_mesh_part->triangles.size();

                auto& new_verts = new_mesh_part->verts;
                auto& temp_verts = temp_mesh_part->verts;
                auto& new_triangles = new_mesh_part->triangles;
                auto& temp_triangles = temp_mesh_part->triangles;

                // Copy over vertices
                new_verts.insert(
                    new_verts.end(),
                    temp_verts.begin(),
                    temp_verts.end());
                // Copy over triangles
                new_triangles.insert(
                    new_triangles.end(),
                    temp_triangles.begin(),
                    temp_triangles.end());

                for (size_t i = triangle_count; i < new_mesh_part->triangles.size(); i++) {
                    // Update the triangle indexes
                    auto& triangle = new_mesh_part->triangles[i];
                    triangle.vert_index_a += vert_count;
                    triangle.vert_index_b += vert_count;
                    triangle.vert_index_c += vert_count;
                    if (temp_mesh.textures.size() <= triangle.texture_index) {
                        throw std::invalid_argument("Texture index is higher than the number of textures.");
                    }
                    const auto& texture_path = temp_mesh.textures[triangle.texture_index];
                    auto it = texture_index_map.find(texture_path);
                    if (it == texture_index_map.end()) {
                        // Texture has not been added yet.
                        size_t texture_index = new_mesh.textures.size();
                        new_mesh.textures.push_back(texture_path);
                        triangle.texture_index = texture_index;
                        texture_index_map[texture_path] = texture_index;
                    } else {
                        triangle.texture_index = it->second;
                    }
                }
            }
        }
    }
    return new_mesh;
}

}

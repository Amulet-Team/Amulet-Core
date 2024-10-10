#pragma once
#include <array>
#include <cmath>
#include <map>
#include <numbers>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace Amulet {

class FloatVec2 {
public:
    float x;
    float y;

    FloatVec2(float x, float y)
        : x(x)
        , y(y)
    {
    }
};

class FloatVec3 {
public:
    float x;
    float y;
    float z;

    FloatVec3(float x, float y, float z)
        : x(x)
        , y(y)
        , z(z)
    {
    }
};

class Vertex {
public:
    // The world coordinate
    FloatVec3 coord;
    // The texture coordinate
    FloatVec2 texture_coord;
    // The tint colour
    FloatVec3 tint;

    Vertex(
        const FloatVec3& coord,
        const FloatVec2& texture_coord,
        const FloatVec3& tint)
        : coord(coord)
        , texture_coord(texture_coord)
        , tint(tint)
    {
    }
};

class Triangle {
public:
    // The indicies of the vertexes in BlockMeshPart::verts.
    size_t vert_index_a;
    size_t vert_index_b;
    size_t vert_index_c;
    // The index of the texture in BlockMesh::textures.
    size_t texture_index;

    Triangle(
        size_t vert_index_a,
        size_t vert_index_b,
        size_t vert_index_c,
        size_t texture_index)
        : vert_index_a(vert_index_a)
        , vert_index_b(vert_index_b)
        , vert_index_c(vert_index_c)
        , texture_index(texture_index)
    {
    }
};

class BlockMeshPart {
public:
    // The vertices in this mesh part.
    std::vector<Vertex> verts;
    // The triangles in this mesh part.
    std::vector<Triangle> triangles;

    BlockMeshPart(): verts(), triangles() {}
    BlockMeshPart(
        const std::vector<Vertex>& verts,
        const std::vector<Triangle>& triangles)
        : verts(verts)
        , triangles(triangles)
    {
    }
};

enum class Transparency {
    // The block is a full block with opaque textures
    FullOpaque,
    // The block is a full block with transparent / translucent textures
    FullTranslucent,
    // The block is not a full block
    Partial
};

enum CullDirection {
    CullNone,
    CullUp,
    CullDown,
    CullNorth,
    CullEast,
    CullSouth,
    CullWest
};

typedef std::map<
    std::pair<std::int8_t, std::int8_t>,
    std::array<CullDirection, 7>>
    RotationCullMapType;

// For every combination of 90 degree rotations in y and x axis
// gives the rotated cull direction.
extern const RotationCullMapType RotationCullMap;

class BlockMesh {
public:
    Transparency transparency;
    std::vector<std::string> textures;
    // The mesh parts. Index matches CullDirection.
    std::array<std::optional<BlockMeshPart>, 7> parts;

    BlockMesh()
        : transparency()
        , textures()
        , parts()
    {
    }
    BlockMesh(
        Transparency transparency,
        const std::vector<std::string>& textures,
        const std::array<std::optional<BlockMeshPart>, 7>& parts)
        : transparency(transparency)
        , textures(textures)
        , parts(parts)
    {
    }

    BlockMesh rotate(std::int8_t rotx, std::int8_t roty) const
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
                float theta_x = std::numbers::pi * rotx / 2.0;
                float theta_y = std::numbers::pi * roty / 2.0;
                float sin_x = std::sinf(theta_x);
                float cos_x = std::cosf(theta_x);
                float sin_y = std::sinf(theta_y);
                float cos_y = std::cosf(theta_y);

                for (std::uint8_t cull_direction = 0; cull_direction < 7; cull_direction++) {
                    // Copy the part to the new cull direction.
                    auto new_cull_direction = cull_map[cull_direction];
                    auto& part = mesh.parts[new_cull_direction] = parts[cull_direction];

                    if (part) {
                        // Rotate the vertex coords.
                        for (auto& vertex : part->verts) {
                            auto& coord = vertex.coord;
                            float x = coord.x - 0.5;
                            float y = coord.y - 0.5;
                            float z = coord.z - 0.5;

                            // Rotate in X axis
                            float y_ = y * cos_x - z * sin_x;
                            z = y * sin_x + z * cos_x;
                            y = y_;

                            // Rotate in Y axis
                            float x_ = x * cos_y + z * sin_y;
                            z = -x * sin_y + z * cos_y;
                            x = x_;

                            coord.x = x + 0.5;
                            coord.y = y + 0.5;
                            coord.z = z + 0.5;
                        }
                    }
                }
                return mesh;
            }
        }
        return *this;
    }
};

 BlockMesh merge_block_meshes(std::vector<std::reference_wrapper<const BlockMesh>>);

}

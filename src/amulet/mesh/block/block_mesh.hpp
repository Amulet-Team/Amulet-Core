#pragma once
#include <array>
#include <cmath>
#include <cstdint>
#include <map>
#include <numbers>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>
#include <functional>

#include <amulet/dll.hpp>
#include <amulet/vector.hpp>

namespace Amulet {

using FloatVec2 = Vec2<float>;
using FloatVec3 = Vec3<float>;

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

enum class BlockMeshTransparency : std::uint8_t {
    // The block is a full block with opaque textures
    FullOpaque,
    // The block is a full block with transparent / translucent textures
    FullTranslucent,
    // The block is not a full block
    Partial
};

enum BlockMeshCullDirection {
    BlockMeshCullNone,
    BlockMeshCullUp,
    BlockMeshCullDown,
    BlockMeshCullNorth,
    BlockMeshCullEast,
    BlockMeshCullSouth,
    BlockMeshCullWest
};

typedef std::map<
    std::pair<std::int8_t, std::int8_t>,
    std::array<BlockMeshCullDirection, 7>>
    RotationCullMapType;

// For every combination of 90 degree rotations in y and x axis
// gives the rotated cull direction.
//extern const RotationCullMapType RotationCullMap;

class BlockMesh {
public:
    BlockMeshTransparency transparency;
    std::vector<std::string> textures;
    // The mesh parts. Index matches BlockMeshCullDirection.
    std::array<std::optional<BlockMeshPart>, 7> parts;

    BlockMesh()
        : transparency()
        , textures()
        , parts()
    {
    }
    BlockMesh(
        BlockMeshTransparency transparency,
        const std::vector<std::string>& textures,
        const std::array<std::optional<BlockMeshPart>, 7>& parts)
        : transparency(transparency)
        , textures(textures)
        , parts(parts)
    {
    }

    AMULET_CORE_EXPORT BlockMesh rotate(std::int8_t rotx, std::int8_t roty) const;
};

AMULET_CORE_EXPORT BlockMesh merge_block_meshes(std::vector<std::reference_wrapper<const BlockMesh>>);

}

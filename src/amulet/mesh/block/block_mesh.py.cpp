#include <memory>

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include <amulet/mesh/block/block_mesh.hpp>
#include <amulet/pybind11/collections.hpp>

namespace py = pybind11;

void init_block_mesh(py::module m_parent)
{
    auto m_mesh = m_parent.def_submodule("mesh");
    auto m = m_mesh.def_submodule("block");

    // FloatVec2
    py::class_<Amulet::FloatVec2> FloatVec2(m, "FloatVec2",
        "A 2D floating point vector");
    FloatVec2.def(
        py::init<
            float,
            float>(),
        py::arg("x"),
        py::arg("y"));
    FloatVec2.def_readwrite("x", &Amulet::FloatVec2::x);
    FloatVec2.def_readwrite("y", &Amulet::FloatVec2::y);

    // FloatVec3
    py::class_<Amulet::FloatVec3> FloatVec3(m, "FloatVec3",
        "A 3D floating point vector");
    FloatVec3.def(
        py::init<
            float,
            float,
            float>(),
        py::arg("x"),
        py::arg("y"),
        py::arg("z"));
    FloatVec3.def_readwrite("x", &Amulet::FloatVec3::x);
    FloatVec3.def_readwrite("y", &Amulet::FloatVec3::y);
    FloatVec3.def_readwrite("z", &Amulet::FloatVec3::z);

    // Vertex
    py::class_<Amulet::Vertex> Vertex(m, "Vertex",
        "Attributes for a single vertex.");
    Vertex.def(
        py::init<
            const Amulet::FloatVec3&,
            const Amulet::FloatVec2&,
            const Amulet::FloatVec3&>(),
        py::arg("coord"),
        py::arg("texture_coord"),
        py::arg("tint"));
    Vertex.def_readwrite("coord", &Amulet::Vertex::coord, py::doc("The spatial coordinate of the vertex."));
    Vertex.def_readwrite("texture_coord", &Amulet::Vertex::texture_coord, py::doc("The texture coordinate of the vertex."));
    Vertex.def_readwrite("tint", &Amulet::Vertex::tint, py::doc("The tint colour for the vertex."));

    // Triangle
    py::class_<Amulet::Triangle> Triangle(m, "Triangle",
        "The vertex and texture indexes that make up a triangle.");
    Triangle.def(
        py::init<
            size_t,
            size_t,
            size_t,
            size_t>(),
        py::arg("vert_index_a"),
        py::arg("vert_index_b"),
        py::arg("vert_index_c"),
        py::arg("texture_index"));
    Triangle.def_readwrite("vert_index_a", &Amulet::Triangle::vert_index_a);
    Triangle.def_readwrite("vert_index_b", &Amulet::Triangle::vert_index_b);
    Triangle.def_readwrite("vert_index_c", &Amulet::Triangle::vert_index_c);
    Triangle.def_readwrite("texture_index", &Amulet::Triangle::texture_index);

    // BlockMeshPart
    py::class_<Amulet::BlockMeshPart> BlockMeshPart(m, "BlockMeshPart",
        "A part of a block mesh for one of the culling directions.");
    BlockMeshPart.def(
        py::init<
            const std::vector<Amulet::Vertex>&,
            const std::vector<Amulet::Triangle>&>(),
        py::arg("verts"),
        py::arg("triangles"));
    BlockMeshPart.def_readwrite("verts", &Amulet::BlockMeshPart::verts, py::doc("The vertices in this block mesh part."));
    BlockMeshPart.def_readwrite("triangles", &Amulet::BlockMeshPart::triangles, py::doc("The triangles in this block mesh part."));

    // BlockMeshTransparency
    py::enum_<Amulet::BlockMeshTransparency>(m, "BlockMeshTransparency",
        "The transparency of a block mesh.")
        .value("FullOpaque", Amulet::BlockMeshTransparency::FullOpaque, "A block that ocupies the whole block and is opaque.")
        .value("FullTranslucent", Amulet::BlockMeshTransparency::FullTranslucent, "A block that ocupies the whole block and has at least one translucent face.")
        .value("Partial", Amulet::BlockMeshTransparency::Partial, "A block that does not ocupy the whole block.");

    // BlockMeshCullDirection
    py::enum_<Amulet::BlockMeshCullDirection>(m, "BlockMeshCullDirection", "The direction a mesh part is culled by. The value corrosponds to the index in the mesh parts array.")
        .value("CullNone", Amulet::BlockMeshCullDirection::CullNone, "Is not culled by any neighbouring blocks.")
        .value("CullUp", Amulet::BlockMeshCullDirection::CullUp, "Is culled by an opaque block above.")
        .value("CullDown", Amulet::BlockMeshCullDirection::CullDown, "Is culled by an opaque block below.")
        .value("CullNorth", Amulet::BlockMeshCullDirection::CullNorth, "Is culled by an opaque block to the north.")
        .value("CullEast", Amulet::BlockMeshCullDirection::CullEast, "Is culled by an opaque block to the east.")
        .value("CullSouth", Amulet::BlockMeshCullDirection::CullSouth, "Is culled by an opaque block to the south.")
        .value("CullWest", Amulet::BlockMeshCullDirection::CullWest, "Is culled by an opaque block to the west.");

    // BlockMesh
    py::class_<Amulet::BlockMesh> BlockMesh(m, "BlockMesh", "All the data that makes up a block mesh.");
    BlockMesh.def(
        py::init<
            Amulet::BlockMeshTransparency,
            std::vector<std::string>,
            std::array<std::optional<Amulet::BlockMeshPart>, 7>>(),
        py::arg("transparency"),
        py::arg("textures"),
        py::arg("parts"));
    BlockMesh.def_readwrite("transparency", &Amulet::BlockMesh::transparency, py::doc("The transparency state of this block mesh."));
    BlockMesh.def_readwrite("textures", &Amulet::BlockMesh::textures, py::doc("The texture paths used in this block mesh. The Triangle's texture_index attribute is an index into this list."));
    BlockMesh.def_readwrite("parts", &Amulet::BlockMesh::parts, py::doc("The mesh parts that make up this mesh. The index corrosponds to the value of BlockMeshCullDirection."));
    BlockMesh.def("rotate", &Amulet::BlockMesh::rotate, py::arg("rotx"), py::arg("roty"), py::doc("Rotate the mesh in the x and y axis. Accepted values are -3 to 3 which corrospond to 90 degree rotations."));

    m.def(
        "merge_block_meshes", [](Amulet::pybind11::collections::Sequence<Amulet::BlockMesh> py_meshes) {
            std::vector<std::reference_wrapper<const Amulet::BlockMesh>> meshes;
            for (auto py_mesh : py_meshes) {
                const auto& mesh = py_mesh.cast<const Amulet::BlockMesh&>();
                meshes.push_back(mesh);
            }
            return Amulet::merge_block_meshes(meshes);
        },
        py::arg("meshes"), py::doc("Merge multiple block mesh objects into one block mesh."));
}

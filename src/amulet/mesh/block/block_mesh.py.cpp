#include <memory>

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include <amulet/mesh/block/block_mesh.hpp>

namespace py = pybind11;

void init_block_mesh(py::module m_parent)
{
    auto m_mesh = m_parent.def_submodule("mesh");
    auto m = m_mesh.def_submodule("block");

    // FloatVec2
    py::class_<Amulet::FloatVec2> FloatVec2(m, "FloatVec2");
    FloatVec2.def(
        py::init<
            float,
            float>(),
        py::arg("x"),
        py::arg("y"));
    FloatVec2.def_readwrite("x", &Amulet::FloatVec2::x);
    FloatVec2.def_readwrite("y", &Amulet::FloatVec2::y);

    // FloatVec3
    py::class_<Amulet::FloatVec3> FloatVec3(m, "FloatVec3");
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
    py::class_<Amulet::Vertex> Vertex(m, "Vertex");
    Vertex.def(
        py::init<
            const Amulet::FloatVec3&,
            const Amulet::FloatVec2&,
            const Amulet::FloatVec3&>(),
        py::arg("coord"),
        py::arg("texture_coord"),
        py::arg("tint"));
    Vertex.def_readwrite("coord", &Amulet::Vertex::coord);
    Vertex.def_readwrite("texture_coord", &Amulet::Vertex::texture_coord);
    Vertex.def_readwrite("tint", &Amulet::Vertex::tint);

    // Triangle
    py::class_<Amulet::Triangle> Triangle(m, "Triangle");
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
    py::class_<Amulet::BlockMeshPart> BlockMeshPart(m, "BlockMeshPart");
    BlockMeshPart.def(
        py::init<
            const std::vector<Amulet::Vertex>&,
            const std::vector<Amulet::Triangle>&>(),
        py::arg("verts"),
        py::arg("triangles"));
    BlockMeshPart.def_readwrite("verts", &Amulet::BlockMeshPart::verts);
    BlockMeshPart.def_readwrite("triangles", &Amulet::BlockMeshPart::triangles);

    // Transparency
    py::enum_<Amulet::Transparency>(m, "Transparency")
        .value("FullOpaque", Amulet::Transparency::FullOpaque)
        .value("FullTranslucent", Amulet::Transparency::FullTranslucent)
        .value("Partial", Amulet::Transparency::Partial);

    // BlockMesh
    py::class_<Amulet::BlockMesh> BlockMesh(m, "BlockMesh");
    BlockMesh.def(
        py::init<
            Amulet::Transparency,
            std::vector<std::string>,
            std::array<std::optional<Amulet::BlockMeshPart>, 7>>(),
        py::arg("transparency"),
        py::arg("textures"),
        py::arg("parts"));
    BlockMesh.def_readwrite("transparency", &Amulet::BlockMesh::transparency);
    BlockMesh.def_readwrite("textures", &Amulet::BlockMesh::textures);
    BlockMesh.def_readwrite("parts", &Amulet::BlockMesh::parts);
    BlockMesh.def("rotate", &Amulet::BlockMesh::rotate, py::arg("rotx"), py::arg("roty"));
}

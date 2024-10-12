from enum import Enum
from turtledemo.sorting_animate import Block
from unittest import TestCase
from amulet.mesh.block import (
    BlockMeshCullDirection,
    BlockMeshTransparency,
    FloatVec2,
    FloatVec3,
    Vertex,
    Triangle,
    BlockMeshPart,
    BlockMesh,
)

class BlockMeshTestCase(TestCase):
    def test_cull_direction(self) -> None:
        self.assertEqual(0, BlockMeshCullDirection.CullNone)
        self.assertEqual(1, BlockMeshCullDirection.CullUp)
        self.assertEqual(2, BlockMeshCullDirection.CullDown)
        self.assertEqual(3, BlockMeshCullDirection.CullNorth)
        self.assertEqual(4, BlockMeshCullDirection.CullEast)
        self.assertEqual(5, BlockMeshCullDirection.CullSouth)
        self.assertEqual(6, BlockMeshCullDirection.CullWest)

        l = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
        ]
        self.assertEqual("0", l[BlockMeshCullDirection.CullNone])

    def test_transparency(self) -> None:
        l = [
            "0",
            "1",
            "2",
        ]
        self.assertEqual("0", l[BlockMeshTransparency.FullOpaque])
        self.assertEqual("1", l[BlockMeshTransparency.FullTranslucent])
        self.assertEqual("2", l[BlockMeshTransparency.Partial])
        self.assertEqual(
            BlockMeshTransparency.FullOpaque,
            min(BlockMeshTransparency.FullOpaque, BlockMeshTransparency.Partial)
        )
        self.assertEqual(
            BlockMeshTransparency.Partial,
            max(BlockMeshTransparency.FullOpaque, BlockMeshTransparency.Partial)
        )

    def test_vec_2(self) -> None:
        vec = FloatVec2(1, 2)
        self.assertAlmostEqual(1.0, vec.x)
        self.assertAlmostEqual(2.0, vec.y)

        vec = FloatVec2(1.1, 2.2)
        self.assertAlmostEqual(1.1, vec.x)
        self.assertAlmostEqual(2.2, vec.y)

    def test_vec_3(self) -> None:
        vec = FloatVec3(1, 2, 3)
        self.assertAlmostEqual(1.0, vec.x)
        self.assertAlmostEqual(2.0, vec.y)
        self.assertAlmostEqual(3.0, vec.z)

        vec = FloatVec3(1.1, 2.2, 3.3)
        self.assertAlmostEqual(1.1, vec.x)
        self.assertAlmostEqual(2.2, vec.y)
        self.assertAlmostEqual(3.3, vec.z)

    def _validate_vertex(self, vertex: Vertex) -> None:
        self.assertAlmostEqual(1.0, vertex.coord.x)
        self.assertAlmostEqual(2.0, vertex.coord.y)
        self.assertAlmostEqual(3.0, vertex.coord.z)
        self.assertAlmostEqual(4.0, vertex.texture_coord.x)
        self.assertAlmostEqual(5.0, vertex.texture_coord.y)
        self.assertAlmostEqual(6.0, vertex.tint.x)
        self.assertAlmostEqual(7.0, vertex.tint.y)
        self.assertAlmostEqual(8.0, vertex.tint.z)

    def test_vertex(self) -> None:
        vertex = Vertex(
            FloatVec3(1, 2, 3),
            FloatVec2(4, 5),
            FloatVec3(6, 7, 8)
        )
        self._validate_vertex(vertex)

    def _validate_triangle(self, triangle: Triangle) -> None:
        self.assertEqual(1, triangle.vert_index_a)
        self.assertEqual(2, triangle.vert_index_b)
        self.assertEqual(3, triangle.vert_index_c)
        self.assertEqual(4, triangle.texture_index)

    def test_triangle(self) -> None:
        triangle = Triangle(1, 2, 3, 4)
        self._validate_triangle(triangle)

    def _validate_part(self, part: BlockMeshPart):
        verts = part.verts
        self.assertIsInstance(verts, list)
        self.assertEqual(1, len(verts))
        vertex = verts[0]
        self._validate_vertex(vertex)

        triangles = part.triangles
        self.assertIsInstance(triangles, list)
        self.assertEqual(1, len(triangles))
        triangle = triangles[0]
        self._validate_triangle(triangle)

    def test_block_mesh_part(self) -> None:
        part = BlockMeshPart([], [])
        self.assertEqual([], part.verts)
        self.assertEqual([], part.triangles)

        part = BlockMeshPart([
            Vertex(
                FloatVec3(1, 2, 3),
                FloatVec2(4, 5),
                FloatVec3(6, 7, 8)
            )
        ], [
            Triangle(1, 2, 3, 4)
        ])
        self._validate_part(part)

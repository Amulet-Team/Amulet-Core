from typing import TypeAlias
import numpy
import itertools

from amulet.mesh.block import (
    BlockMesh,
    BlockMeshPart,
    Triangle,
    Vertex,
    FloatVec3,
    FloatVec2,
    BlockMeshTransparency,
    BlockMeshCullDirection,
)

BoundsType: TypeAlias = tuple[
    tuple[float, float], tuple[float, float], tuple[float, float]
]
TextureUVType: TypeAlias = tuple[
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
]

UNIT_BOX_COORDINATES = numpy.array(
    list(itertools.product((0, 1), (0, 1), (0, 1)))
)  # X, Y, Z

CULL_DIRECTION_NAMES = (
    "down",
    "up",
    "north",
    "east",
    "south",
    "west",
)

# This maps face direction to the vertices used (defined in UNIT_BOX_COORDINATES)
VERTEX_INDEXES = (
    numpy.array([0, 4, 5, 1]),
    numpy.array([3, 7, 6, 2]),
    numpy.array([4, 0, 2, 6]),
    numpy.array([5, 4, 6, 7]),
    numpy.array([1, 5, 7, 3]),
    numpy.array([0, 1, 3, 2]),
)

# This maps face direction to the vertices used (defined in UNIT_BOX_COORDINATES)
CUBE_FACE_LUT = dict(zip(CULL_DIRECTION_NAMES, VERTEX_INDEXES))

TRI_FACE = numpy.array([0, 1, 2, 0, 2, 3], numpy.uint32)

# cube_vert_lut = {  # This maps from vertex index to index in [minx, miny, minz, maxx, maxy, maxz]
# 	1: [0, 1, 5],
# 	3: [0, 4, 5],
# 	0: [0, 1, 2],
# 	2: [0, 4, 2],
# 	5: [3, 1, 5],
# 	7: [3, 4, 5],
# 	4: [3, 1, 2],
# 	6: [3, 4, 2],
# }
#
# # combines the above two to map from face to index in [minx, miny, minz, maxx, maxy, maxz]. Used to index a numpy array
# # The above two have been kept separate because the merged result is unintuitive and difficult to edit.
# cube_lut = {
# 	face_dir_: [
# 		vert_coord_ for vert_ in vert_index_ for vert_coord_ in cube_vert_lut[vert_]
# 	]
# 	for face_dir_, vert_index_ in CUBE_FACE_LUT.items()
# }

UV_ROTATION_LUT = [0, 3, 2, 3, 2, 1, 0, 1]  # remap


# tvert_lut = {  # TODO: implement this for the cases where the UV is not defined
# 	'down': [],
# 	'up': [],
# 	'north': [],
# 	'east': [],
# 	'south': [],
# 	'west': []
# }


def get_cube(
    down: str,
    up: str,
    north: str,
    east: str,
    south: str,
    west: str,
    transparency: BlockMeshTransparency = BlockMeshTransparency.FullOpaque,
    tint: tuple[int, int, int] = (1, 1, 1),
    bounds: BoundsType = ((0, 1), (0, 1), (0, 1)),
    texture_uv: TextureUVType = ((0, 0, 1, 1),) * 6,
    do_not_cull: tuple[bool, bool, bool, bool, bool, bool] = (
        False,
        False,
        False,
        False,
        False,
        False,
    ),
) -> BlockMesh:
    texture_paths: dict[str, int] = {}
    mesh_parts: list[tuple[list[Vertex], list[Triangle]] | None] = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    box_coordinates = list(itertools.product(*bounds))
    tint_vec = FloatVec3(*tint)

    for (
        cull_direction,
        vertex_index,
        do_not_cull_face,
        texture_path,
        texture_coords,
    ) in zip(
        (
            BlockMeshCullDirection.CullDown,
            BlockMeshCullDirection.CullUp,
            BlockMeshCullDirection.CullNorth,
            BlockMeshCullDirection.CullEast,
            BlockMeshCullDirection.CullSouth,
            BlockMeshCullDirection.CullWest,
        ),
        VERTEX_INDEXES,
        do_not_cull,
        (down, up, north, east, south, west),
        texture_uv,
    ):
        # Get the index of the texture path. Add if it is not contained.
        texture_index = texture_paths.setdefault(texture_path, len(texture_paths))
        if do_not_cull_face:
            cull_direction = BlockMeshCullDirection.CullNone
        part = mesh_parts[cull_direction]
        if part is None:
            mesh_parts[cull_direction] = part = ([], [])
        verts, tris = part
        vert_count = len(verts)

        for i in range(4):
            x, y, z = box_coordinates[vertex_index[i]]
            uvx = texture_coords[UV_ROTATION_LUT[i * 2]]
            uvy = texture_coords[UV_ROTATION_LUT[i * 2 + 1]]
            verts.append(
                Vertex(
                    FloatVec3(x, y, z),
                    FloatVec2(uvx, uvy),
                    tint_vec,
                )
            )
        for a, b, c in TRI_FACE.reshape((2, 3)):
            tris.append(
                Triangle(a + vert_count, b + vert_count, c + vert_count, texture_index)
            )

    return BlockMesh(
        transparency,
        list(texture_paths),
        [None if part is None else BlockMeshPart(*part) for part in mesh_parts],
    )


def get_unit_cube(
    down: str,
    up: str,
    north: str,
    east: str,
    south: str,
    west: str,
    transparency: BlockMeshTransparency = BlockMeshTransparency.FullOpaque,
    tint: tuple[int, int, int] = (1, 1, 1),
) -> BlockMesh:
    return get_cube(down, up, north, east, south, west, transparency, tint)

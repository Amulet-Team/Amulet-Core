from typing import Optional
import numpy
import itertools

from amulet.mesh.block.block_mesh import BlockMesh, Transparency

BoundsType = tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
TextureUVType = tuple[
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
]


unit_box_coordinates = numpy.array(
    list(itertools.product((0, 1), (0, 1), (0, 1)))
)  # X, Y, Z
cube_face_lut = (
    {  # This maps face direction to the vertices used (defined in unit_box_coordinates)
        "down": numpy.array([0, 4, 5, 1]),
        "up": numpy.array([3, 7, 6, 2]),
        "north": numpy.array([4, 0, 2, 6]),
        "east": numpy.array([5, 4, 6, 7]),
        "south": numpy.array([1, 5, 7, 3]),
        "west": numpy.array([0, 1, 3, 2]),
    }
)
tri_face = numpy.array([0, 1, 2, 0, 2, 3], numpy.uint32)

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
# 	for face_dir_, vert_index_ in cube_face_lut.items()
# }

uv_rotation_lut = [0, 3, 2, 3, 2, 1, 0, 1]  # remap


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
    transparency: Transparency = Transparency.FullOpaque,
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
    box_coordinates = numpy.array(list(itertools.product(*bounds)))
    _texture_uv: dict[Optional[str], numpy.ndarray] = {
        face: numpy.array(texture_uv[i], float) for i, face in enumerate(cube_face_lut)
    }
    _verts: dict[Optional[str], numpy.ndarray] = {}
    _texture_coords: dict[Optional[str], numpy.ndarray] = {}
    _tint_verts: dict[Optional[str], numpy.ndarray] = {}
    _tri_faces: dict[Optional[str], numpy.ndarray] = {}
    for _face_dir in cube_face_lut:
        _verts[_face_dir] = box_coordinates[
            cube_face_lut[_face_dir]
        ].ravel()  # vertex coordinates for this face
        _texture_coords[_face_dir] = _texture_uv[_face_dir][
            uv_rotation_lut
        ]  # texture vertices
        _tint_verts[_face_dir] = numpy.full((4, 3), tint, dtype=float).ravel()
        _tri_faces[_face_dir] = tri_face

    texture_paths_arr, texture_index = numpy.unique(
        (down, up, north, east, south, west), return_inverse=True
    )
    texture_paths = tuple(texture_paths_arr)
    _tri_texture_index: dict[Optional[str], numpy.ndarray] = {
        side: numpy.full(2, texture_index[side_index], dtype=numpy.uint32)
        for side_index, side in enumerate(cube_face_lut)
    }

    if any(do_not_cull):
        do_not_cull_faces = tuple(
            face for face, not_cull in zip(cube_face_lut, do_not_cull) if not_cull
        )
        for obj in (_verts, _texture_coords, _tint_verts, _tri_texture_index):
            obj[None] = numpy.concatenate([obj[key] for key in do_not_cull_faces])
            for key in do_not_cull_faces:
                del obj[key]
        _tri_faces[None] = numpy.concatenate(
            [_tri_faces[key] + 4 * i for i, key in enumerate(do_not_cull_faces)]
        )
        for key in do_not_cull_faces:
            del _tri_faces[key]

    return BlockMesh(
        3,
        _verts,
        _texture_coords,
        _tint_verts,
        _tri_faces,
        _tri_texture_index,
        texture_paths,
        transparency,
    )


def get_unit_cube(
    down: str,
    up: str,
    north: str,
    east: str,
    south: str,
    west: str,
    transparency: Transparency = Transparency.FullOpaque,
    tint: tuple[int, int, int] = (1, 1, 1),
) -> BlockMesh:
    return get_cube(down, up, north, east, south, west, transparency, tint)

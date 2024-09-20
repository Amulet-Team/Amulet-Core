from _typeshed import Incomplete
from amulet.mesh.block.block_mesh import BlockMesh as BlockMesh
from amulet.mesh.block.block_mesh import Transparency as Transparency

BoundsType = tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
TextureUVType = tuple[
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
]
unit_box_coordinates: Incomplete
cube_face_lut: Incomplete
tri_face: Incomplete
uv_rotation_lut: Incomplete

def get_cube(
    down: str,
    up: str,
    north: str,
    east: str,
    south: str,
    west: str,
    transparency: Transparency = ...,
    tint: tuple[int, int, int] = (1, 1, 1),
    bounds: BoundsType = ((0, 1), (0, 1), (0, 1)),
    texture_uv: TextureUVType = ...,
    do_not_cull: tuple[bool, bool, bool, bool, bool, bool] = (
        False,
        False,
        False,
        False,
        False,
        False,
    ),
) -> BlockMesh: ...
def get_unit_cube(
    down: str,
    up: str,
    north: str,
    east: str,
    south: str,
    west: str,
    transparency: Transparency = ...,
    tint: tuple[int, int, int] = (1, 1, 1),
) -> BlockMesh: ...

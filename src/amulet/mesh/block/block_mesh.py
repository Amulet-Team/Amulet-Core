from __future__ import annotations
from typing import Optional, Any
from collections.abc import Iterable
import numpy
import itertools
from enum import IntEnum

from amulet.mesh.util import rotate_3d

FACE_KEYS = {"down", "up", "north", "east", "south", "west", None}


def _create_cull_map() -> dict[tuple[int, int], dict[Optional[str], Optional[str]]]:
    cull_remap_ = {}
    roty_map = ["north", "east", "south", "west"]
    for roty in range(-3, 4):
        for rotx in range(-3, 4):
            roty_map_rotated = roty_map[roty:] + roty_map[:roty]
            rotx_map = [roty_map_rotated[0], "down", roty_map_rotated[2], "up"]
            rotx_map_rotated = rotx_map[rotx:] + rotx_map[:rotx]
            roty_remap = dict(zip(roty_map, roty_map_rotated))
            rotx_remap = dict(zip(rotx_map, rotx_map_rotated))
            cull_remap_value: dict[Optional[str], Optional[str]] = {}
            cull_remap_[(roty, rotx)] = cull_remap_value
            for key in FACE_KEYS:
                if key is None:
                    cull_remap_value[key] = None
                else:
                    roty_value = roty_remap.get(key, key)
                    cull_remap_value[key] = rotx_remap.get(roty_value, roty_value)
    return cull_remap_


cull_remap_all = _create_cull_map()


class Transparency(IntEnum):
    FullOpaque = 0  # the block is a full block with opaque textures
    FullTranslucent = (
        1  # the block is a full block with transparent/translucent textures
    )
    Partial = 2  # the block is not a full block


class BlockMesh:
    """Class for storing model data"""

    @classmethod
    def merge(cls, models: Iterable[BlockMesh]) -> BlockMesh:
        textures_src: list[str] = []
        texture_count = 0
        vert_count: dict[Optional[str], int] = {side: 0 for side in FACE_KEYS}
        verts_src: dict[Optional[str], list[numpy.ndarray]] = {
            side: [] for side in FACE_KEYS
        }
        tverts_src: dict[Optional[str], list[numpy.ndarray]] = {
            side: [] for side in FACE_KEYS
        }
        tint_verts_src: dict[Optional[str], list[numpy.ndarray]] = {
            side: [] for side in FACE_KEYS
        }
        faces_src: dict[Optional[str], list[numpy.ndarray]] = {
            side: [] for side in FACE_KEYS
        }
        texture_indexes_src: dict[Optional[str], list[numpy.ndarray]] = {
            side: [] for side in FACE_KEYS
        }
        transparent: Transparency = Transparency.Partial

        cull_dir: Optional[str]
        for temp_model in models:
            for cull_dir in temp_model.faces.keys():
                verts_src[cull_dir].append(temp_model.verts[cull_dir])
                tverts_src[cull_dir].append(temp_model.texture_coords[cull_dir])
                tint_verts_src[cull_dir].append(temp_model.tint_verts[cull_dir])
                face_table = temp_model.faces[cull_dir].copy()
                texture_index = temp_model.texture_index[cull_dir].copy()
                face_table += vert_count[cull_dir]
                texture_index += texture_count
                faces_src[cull_dir].append(face_table)
                texture_indexes_src[cull_dir].append(texture_index)

                vert_count[cull_dir] += int(
                    temp_model.verts[cull_dir].shape[0] / temp_model.face_mode
                )

            textures_src += temp_model.textures
            texture_count += len(temp_model.textures)
            transparent = min(transparent, temp_model.is_transparent)

        if textures_src:
            textures_, texture_index_map = numpy.unique(
                textures_src, return_inverse=True, axis=0
            )
            textures = tuple(textures_)
            texture_index_map = texture_index_map.astype(numpy.uint32)
        else:
            textures = ()
            texture_index_map = numpy.array([], dtype=numpy.uint8)

        verts: dict[Optional[str], numpy.ndarray] = {}
        tverts: dict[Optional[str], numpy.ndarray] = {}
        tint_verts: dict[Optional[str], numpy.ndarray] = {}
        faces: dict[Optional[str], numpy.ndarray] = {}
        texture_indexes: dict[Optional[str], numpy.ndarray] = {}

        for cull_dir in FACE_KEYS:
            if faces_src[cull_dir]:
                faces[cull_dir] = numpy.concatenate(faces_src[cull_dir], axis=None)
                texture_indexes[cull_dir] = texture_index_map[
                    numpy.concatenate(texture_indexes_src[cull_dir], axis=None)
                ]
                if verts_src[cull_dir]:
                    verts[cull_dir] = numpy.concatenate(verts_src[cull_dir], axis=None)
                    tverts[cull_dir] = numpy.concatenate(
                        tverts_src[cull_dir], axis=None
                    )
                    tint_verts[cull_dir] = numpy.concatenate(
                        tint_verts_src[cull_dir], axis=None
                    )
                else:
                    verts[cull_dir] = numpy.zeros((0, 3), float)
                    tverts[cull_dir] = numpy.zeros((0, 2), float)
                    tint_verts[cull_dir] = numpy.zeros(0, float)

        return cls(
            3, verts, tverts, tint_verts, faces, texture_indexes, textures, transparent
        )

    def __init__(
        self,
        face_width: int,
        verts: dict[Optional[str], numpy.ndarray],
        texture_coords: dict[Optional[str], numpy.ndarray],
        tint_verts: dict[Optional[str], numpy.ndarray],
        # normals: dict[Optional[str], numpy.ndarray],
        faces: dict[Optional[str], numpy.ndarray],
        texture_index: dict[Optional[str], numpy.ndarray],
        textures: tuple[str, ...],
        transparency: Transparency,
    ):
        """

        :param face_width: the number of vertices per face (3 or 4)
        :param verts: a numpy float array containing the vert data. One line per vertex
        :param texture_coords: a numpy float array containing the texture coordinate data. One line per vertex
        :param tint_verts: a numpy bool array if the vertex should have a tint applied to it. One line per vertex
        :param faces: a dictionary of numpy int arrays (stored under cull direction) containing
            the vertex indexes (<face_width> columns) and
            texture index (1 column)
        :param texture_index:
        :param textures:
        :param transparency: is the model a full non-transparent block

        Workflow:
            find the directions a block is not being culled in
            look them up in the face table
            the face table will tell you which vertices are needed for the face
        """
        assert isinstance(verts, dict) and all(
            key in FACE_KEYS
            and isinstance(val, numpy.ndarray)
            and val.ndim == 1
            and val.shape[0] % 3 == 0
            for key, val in verts.items()
        ), "The format for verts is incorrect"

        assert isinstance(texture_coords, dict) and all(
            key in FACE_KEYS
            and isinstance(val, numpy.ndarray)
            and val.ndim == 1
            and val.shape[0] % 2 == 0
            for key, val in texture_coords.items()
        ), "The format for texture coords is incorrect"

        assert isinstance(tint_verts, dict) and all(
            key in FACE_KEYS
            and isinstance(val, numpy.ndarray)
            and val.ndim == 1
            and val.shape[0] % 3 == 0
            for key, val in tint_verts.items()
        ), "The format of tint verts is incorrect"

        assert isinstance(faces, dict) and all(
            key in FACE_KEYS
            and isinstance(val, numpy.ndarray)
            and numpy.issubdtype(val.dtype, numpy.unsignedinteger)
            and val.ndim == 1
            and val.shape[0] % face_width == 0
            for key, val in faces.items()
        ), "The format of faces is incorrect"

        assert isinstance(texture_index, dict) and all(
            key in FACE_KEYS
            and isinstance(val, numpy.ndarray)
            and numpy.issubdtype(val.dtype, numpy.unsignedinteger)
            and val.ndim == 1
            and val.shape[0] == faces[key].shape[0] / face_width
            for key, val in texture_index.items()
        ), "The format of texture index is incorrect"

        assert isinstance(textures, Iterable) and all(
            isinstance(texture, str) for texture in textures
        ), "The format of the textures is incorrect"

        self._face_mode = face_width
        self._verts = verts
        self._texture_coords = texture_coords
        self._tint_verts = tint_verts
        self._vert_tables: Optional[dict[Optional[str], numpy.ndarray]] = None

        self._faces = faces
        self._texture_index = texture_index
        self._textures = tuple(textures)
        self._transparency = transparency

        for array in itertools.chain(
            self._verts.values(),
            self._texture_coords.values(),
            self._faces.values(),
            self._texture_index.values(),
        ):
            array.setflags(write=False)

    @property
    def face_mode(self) -> int:
        """The number of vertices per face"""
        return self._face_mode

    @property
    def vert_tables(self) -> dict[Optional[str], numpy.ndarray]:
        """A dictionary of cull dir -> the flat vert table containing vertices, texture coords and (in the future) normals"""
        if self._vert_tables is None:
            self._vert_tables = {
                key: numpy.hstack(
                    (
                        self._verts[key].reshape(-1, self._face_mode),
                        self._texture_coords[key].reshape(-1, 2),
                        # TODO: add in face normals
                    )
                ).ravel()
                for key in self._verts.keys()
            }
            for array in self._vert_tables.values():
                array.setflags(write=False)
        return self._vert_tables

    @property
    def verts(self) -> dict[Optional[str], numpy.ndarray]:
        """A dictionary mapping face cull direction to the vertex table for that direction.
        The vertex table is a flat numpy array who's length is a multiple of 3.
        x,y,z coordinates."""
        return self._verts

    @property
    def texture_coords(self) -> dict[Optional[str], numpy.ndarray]:
        """A dictionary mapping face cull direction to the texture coords table for that direction.
        The texture coords table is a flat numpy array who's length is a multiple of 2.
        tx, ty"""
        return self._texture_coords

    @property
    def tint_verts(self) -> dict[Optional[str], numpy.ndarray]:
        """A dictionary mapping face cull direction to the tint table for that direction.
        The tint table is a flat numpy bool array with three values per vertex.
        """
        return self._tint_verts

    @property
    def faces(self) -> dict[Optional[str], numpy.ndarray]:
        """A dictionary mapping face cull direction to the face table for that direction.
        The face table is a flat numpy array of multiple 3 or 4 depending on face_mode.
        First 3 or 4 columns index into the verts table.
        Last column indexes into textures."""
        return self._faces

    @property
    def texture_index(self) -> dict[Optional[str], numpy.ndarray]:
        """A dictionary mapping face cull direction to the face table for that direction.
        The face table is a flat numpy array of multiple 2 indexing into textures."""
        return self._texture_index

    @property
    def textures(self) -> tuple[str, ...]:
        """A list of all the texture paths."""
        return self._textures

    @property
    def is_opaque(self) -> bool:
        """
        If the model covers all surrounding blocks.
        Also takes into account texture transparency.
        """
        return not self._transparency

    @property
    def is_transparent(self) -> Transparency:
        """
        The transparency mode of the block
        0 - the block is a full block with opaque textures
        1 - the block is a full block with transparent/translucent textures
        2 - the block is not a full block
        """
        return self._transparency

    def rotate(self, rotx: int, roty: int) -> BlockMesh:
        """Create a rotated version of this block model. Culling directions are also rotated.
        rotx and roty must be ints in the range -3 to 3 inclusive."""
        if rotx or roty and (roty, rotx) in cull_remap_all:
            cull_remap = cull_remap_all[(roty, rotx)]
            return BlockMesh(
                self.face_mode,
                {
                    cull_remap[cull_dir]: rotate_3d(
                        rotate_3d(
                            self.verts[cull_dir].reshape((-1, self.face_mode)),
                            rotx * 90,
                            0,
                            0,
                            0.5,
                            0.5,
                            0.5,
                        ),
                        0,
                        roty * 90,
                        0,
                        0.5,
                        0.5,
                        0.5,
                    ).ravel()
                    for cull_dir in self.verts
                },
                {
                    cull_remap[cull_dir]: self.texture_coords[cull_dir]
                    for cull_dir in self.texture_coords
                },
                {
                    cull_remap[cull_dir]: self.tint_verts[cull_dir]
                    for cull_dir in self.tint_verts
                },
                {cull_remap[cull_dir]: self.faces[cull_dir] for cull_dir in self.faces},
                {
                    cull_remap[cull_dir]: self.texture_index[cull_dir]
                    for cull_dir in self.texture_index
                },
                self.textures,
                self.is_transparent,
            )
        return self

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BlockMesh):
            return NotImplemented
        return (
            self.face_mode == other.face_mode
            and all(
                obj1.keys() == obj2.keys()
                and all(numpy.array_equal(obj1[key], obj2[key]) for key in obj1.keys())
                for obj1, obj2 in (
                    (self.verts, other.verts),
                    (self.texture_coords, other.texture_coords),
                    (self.tint_verts, other.tint_verts),
                    (self.faces, other.faces),
                    (self.texture_index, other.texture_index),
                )
            )
            and self.textures == other.textures
            and self.is_transparent == other.is_transparent
        )

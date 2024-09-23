import os
import json
import copy
from typing import Union, Iterable, Iterator, Optional
from PIL import Image
import numpy
import glob
import itertools
import logging
import re

import amulet_nbt

from amulet.block import Block
from amulet.resource_pack import BaseResourcePackManager
from amulet.resource_pack.java import JavaResourcePack
from amulet.mesh.block.block_mesh import (
    BlockMesh,
    FACE_KEYS,
    Transparency,
)
from amulet.mesh.util import rotate_3d
from amulet.mesh.block.cube import (
    cube_face_lut,
    uv_rotation_lut,
    tri_face,
)

log = logging.getLogger(__name__)


UselessImageGroups = {
    "colormap",
    "effect",
    "environment",
    "font",
    "gui",
    "map",
    "mob_effect",
    "particle",
}

_PropertiesPattern = re.compile(r"(?P<name>[a-zA-Z0-9_]+)=(?P<value>[a-zA-Z0-9_]+),?")


class JavaResourcePackManager(BaseResourcePackManager[JavaResourcePack]):
    """A class to load and handle the data from the packs.
    Packs are given as a list with the later packs overwriting the earlier ones."""

    def __init__(
        self,
        resource_packs: Union[JavaResourcePack, Iterable[JavaResourcePack]],
        load: bool = True,
    ) -> None:
        super().__init__()
        self._blockstate_files: dict[tuple[str, str], dict] = {}
        self._textures: dict[tuple[str, str], str] = {}
        self._texture_is_transparent: dict[str, tuple[float, bool]] = {}
        self._model_files: dict[tuple[str, str], dict] = {}
        if isinstance(resource_packs, Iterable):
            self._packs = list(resource_packs)
        elif isinstance(resource_packs, JavaResourcePack):
            self._packs = [resource_packs]
        else:
            raise Exception(f"Invalid format {resource_packs}")
        if load:
            for _ in self.reload():
                pass

    def _unload(self) -> None:
        """Clear all loaded resources."""
        super()._unload()
        self._blockstate_files.clear()
        self._textures.clear()
        self._texture_is_transparent.clear()
        self._model_files.clear()

    def _load_iter(self) -> Iterator[float]:
        blockstate_file_paths: dict[tuple[str, str], str] = {}
        model_file_paths: dict[tuple[str, str], str] = {}

        transparency_cache_path = os.path.join(
            os.environ["CACHE_DIR"], "resource_packs", "java", "transparency_cache.json"
        )
        self._load_transparency_cache(transparency_cache_path)

        self._textures[("minecraft", "missing_no")] = self.missing_no

        pack_count = len(self._packs)

        for pack_index, pack in enumerate(self._packs):
            # pack_format=2 textures/blocks, textures/items - case sensitive
            # pack_format=3 textures/blocks, textures/items - lower case
            # pack_format=4 textures/block, textures/item
            # pack_format=5 model paths and texture paths are now optionally namespaced

            pack_progress = pack_index / pack_count
            yield pack_progress

            if pack.valid_pack and pack.pack_format >= 2:
                image_paths = glob.glob(
                    os.path.join(
                        glob.escape(pack.root_dir),
                        "assets",
                        "*",  # namespace
                        "textures",
                        "**",
                        "*.png",
                    ),
                    recursive=True,
                )
                image_count = len(image_paths)
                sub_progress = pack_progress
                for image_index, texture_path in enumerate(image_paths):
                    _, namespace, _, *rel_path_list = os.path.normpath(
                        os.path.relpath(texture_path, pack.root_dir)
                    ).split(os.sep)
                    if rel_path_list[0] not in UselessImageGroups:
                        rel_path = "/".join(rel_path_list)[:-4]
                        self._textures[(namespace, rel_path)] = texture_path
                        if (
                            os.stat(texture_path).st_mtime
                            != self._texture_is_transparent.get(texture_path, [0])[0]
                        ):
                            im: Image.Image = Image.open(texture_path)
                            if im.mode == "RGBA":
                                alpha = numpy.array(im.getchannel("A").getdata())
                                texture_is_transparent = bool(numpy.any(alpha != 255))
                            else:
                                texture_is_transparent = False

                            self._texture_is_transparent[texture_path] = (
                                os.stat(texture_path).st_mtime,
                                texture_is_transparent,
                            )
                    yield sub_progress + image_index / (image_count * pack_count * 3)

                blockstate_paths = glob.glob(
                    os.path.join(
                        glob.escape(pack.root_dir),
                        "assets",
                        "*",  # namespace
                        "blockstates",
                        "*.json",
                    )
                )
                blockstate_count = len(blockstate_paths)
                sub_progress = pack_progress + 1 / (pack_count * 3)
                for blockstate_index, blockstate_path in enumerate(blockstate_paths):
                    _, namespace, _, blockstate_file = os.path.normpath(
                        os.path.relpath(blockstate_path, pack.root_dir)
                    ).split(os.sep)
                    blockstate_file_paths[(namespace, blockstate_file[:-5])] = (
                        blockstate_path
                    )
                    yield sub_progress + (blockstate_index) / (
                        blockstate_count * pack_count * 3
                    )

                model_paths = glob.glob(
                    os.path.join(
                        glob.escape(pack.root_dir),
                        "assets",
                        "*",  # namespace
                        "models",
                        "**",
                        "*.json",
                    ),
                    recursive=True,
                )
                model_count = len(model_paths)
                sub_progress = pack_progress + 2 / (pack_count * 3)
                for model_index, model_path in enumerate(model_paths):
                    _, namespace, _, *rel_path_list = os.path.normpath(
                        os.path.relpath(model_path, pack.root_dir)
                    ).split(os.sep)
                    rel_path = "/".join(rel_path_list)[:-5]
                    model_file_paths[(namespace, rel_path.replace(os.sep, "/"))] = (
                        model_path
                    )
                    yield sub_progress + (model_index) / (model_count * pack_count * 3)

        os.makedirs(os.path.dirname(transparency_cache_path), exist_ok=True)
        with open(transparency_cache_path, "w") as f:
            json.dump(self._texture_is_transparent, f)

        for key, path in blockstate_file_paths.items():
            with open(path) as fi:
                try:
                    self._blockstate_files[key] = json.load(fi)
                except json.JSONDecodeError:
                    log.error(f"Failed to parse blockstate file {path}")

        for key, path in model_file_paths.items():
            with open(path) as fi:
                try:
                    self._model_files[key] = json.load(fi)
                except json.JSONDecodeError:
                    log.error(f"Failed to parse model file file {path}")

    @property
    def textures(self) -> tuple[str, ...]:
        """Returns a tuple of all the texture paths in the resource pack."""
        return tuple(self._textures.values())

    def get_texture_path(self, namespace: Optional[str], relative_path: str) -> str:
        """Get the absolute texture path from the namespace and relative path pair"""
        if namespace is None:
            return self.missing_no
        key = (namespace, relative_path)
        if key in self._textures:
            return self._textures[key]
        else:
            return self.missing_no

    @staticmethod
    def parse_state_val(val: Union[str, bool]) -> list:
        """Convert the json block state format into a consistent format."""
        if isinstance(val, str):
            return [amulet_nbt.TAG_String(v) for v in val.split("|")]
        elif isinstance(val, bool):
            return [
                amulet_nbt.TAG_String("true") if val else amulet_nbt.TAG_String("false")
            ]
        else:
            raise Exception(f"Could not parse state val {val}")

    def _get_model(self, block: Block) -> BlockMesh:
        """Find the model paths for a given block state and load them."""
        if (block.namespace, block.base_name) in self._blockstate_files:
            blockstate: dict = self._blockstate_files[
                (block.namespace, block.base_name)
            ]
            if "variants" in blockstate:
                for variant in blockstate["variants"]:
                    if variant == "":
                        try:
                            return self._load_blockstate_model(
                                blockstate["variants"][variant]
                            )
                        except Exception as e:
                            log.error(
                                f"Failed to load block model {blockstate['variants'][variant]}\n{e}"
                            )
                    else:
                        properties_match = _PropertiesPattern.finditer(f",{variant}")
                        if all(
                            block.properties.get(
                                match.group("name"),
                                amulet_nbt.TAG_String(match.group("value")),
                            ).py_data
                            == match.group("value")
                            for match in properties_match
                        ):
                            try:
                                return self._load_blockstate_model(
                                    blockstate["variants"][variant]
                                )
                            except Exception as e:
                                log.error(
                                    f"Failed to load block model {blockstate['variants'][variant]}\n{e}"
                                )

            elif "multipart" in blockstate:
                models = []

                for case in blockstate["multipart"]:
                    try:
                        if "when" in case:
                            if "OR" in case["when"]:
                                if not any(
                                    all(
                                        block.properties.get(prop, None)
                                        in self.parse_state_val(val)
                                        for prop, val in prop_match.items()
                                    )
                                    for prop_match in case["when"]["OR"]
                                ):
                                    continue
                            elif "AND" in case["when"]:
                                if not all(
                                    all(
                                        block.properties.get(prop, None)
                                        in self.parse_state_val(val)
                                        for prop, val in prop_match.items()
                                    )
                                    for prop_match in case["when"]["AND"]
                                ):
                                    continue
                            elif not all(
                                block.properties.get(prop, None)
                                in self.parse_state_val(val)
                                for prop, val in case["when"].items()
                            ):
                                continue

                        if "apply" in case:
                            try:
                                models.append(
                                    self._load_blockstate_model(case["apply"])
                                )

                            except Exception as e:
                                log.error(
                                    f"Failed to load block model {case['apply']}\n{e}"
                                )
                    except Exception as e:
                        log.error(f"Failed to parse block state for {block}\n{e}")

                return BlockMesh.merge(models)

        return self.missing_block

    def _load_blockstate_model(
        self, blockstate_value: Union[dict, list[dict]]
    ) -> BlockMesh:
        """Load the model(s) associated with a block state and apply rotations if needed."""
        if isinstance(blockstate_value, list):
            blockstate_value = blockstate_value[0]
        if "model" not in blockstate_value:
            return self.missing_block
        model_path = blockstate_value["model"]
        rotx = int(blockstate_value.get("x", 0) // 90)
        roty = int(blockstate_value.get("y", 0) // 90)
        uvlock = blockstate_value.get("uvlock", False)

        model = copy.deepcopy(self._load_block_model(model_path))

        # TODO: rotate model based on uv_lock
        return model.rotate(rotx, roty)

    def _load_block_model(self, model_path: str) -> BlockMesh:
        """Load the model file associated with the Block and convert to a BlockMesh."""
        # recursively load model files into one dictionary
        java_model = self._recursive_load_block_model(model_path)

        # set up some variables
        texture_dict = {}
        textures = []
        texture_count = 0
        vert_count = {side: 0 for side in FACE_KEYS}
        verts_src: dict[Optional[str], list[numpy.ndarray]] = {
            side: [] for side in FACE_KEYS
        }
        tverts_src: dict[Optional[str], list[numpy.ndarray]] = {
            side: [] for side in FACE_KEYS
        }
        tint_verts_src: dict[Optional[str], list[float]] = {
            side: [] for side in FACE_KEYS
        }
        faces_src: dict[Optional[str], list[numpy.ndarray]] = {
            side: [] for side in FACE_KEYS
        }

        texture_indexes_src: dict[Optional[str], list[int]] = {
            side: [] for side in FACE_KEYS
        }
        transparent = Transparency.Partial

        if java_model.get("textures", {}) and not java_model.get("elements"):
            return self.missing_block

        for element in java_model.get("elements", {}):
            # iterate through elements (one cube per element)
            element_faces = element.get("faces", {})

            opaque_face_count = 0
            if (
                transparent
                and "rotation" not in element
                and element.get("to", [16, 16, 16]) == [16, 16, 16]
                and element.get("from", [0, 0, 0]) == [0, 0, 0]
                and len(element_faces) >= 6
            ):
                # if the block is not yet defined as a solid block
                # and this element is a full size element
                # check if the texture is opaque
                transparent = Transparency.FullTranslucent
                check_faces = True
            else:
                check_faces = False

            # lower and upper box coordinates
            corners = numpy.sort(
                numpy.array(
                    [element.get("to", [16, 16, 16]), element.get("from", [0, 0, 0])],
                    float,
                )
                / 16,
                0,
            )

            # vertex coordinates of the box
            box_coordinates = numpy.array(
                list(itertools.product(corners[:, 0], corners[:, 1], corners[:, 2]))
            )

            for face_dir in element_faces:
                if face_dir in cube_face_lut:
                    # get the cull direction. If there is an opaque block in this direction then cull this face
                    cull_dir = element_faces[face_dir].get("cullface", None)
                    if cull_dir not in FACE_KEYS:
                        cull_dir = None

                    # get the relative texture path for the texture used
                    texture_relative_path = element_faces[face_dir].get("texture", None)
                    while isinstance(
                        texture_relative_path, str
                    ) and texture_relative_path.startswith("#"):
                        texture_relative_path = java_model["textures"].get(
                            texture_relative_path[1:], None
                        )
                    texture_path_list = texture_relative_path.split(":", 1)
                    if len(texture_path_list) == 2:
                        namespace, texture_relative_path = texture_path_list
                    else:
                        namespace = "minecraft"

                    texture_path = self.get_texture_path(
                        namespace, texture_relative_path
                    )

                    if check_faces:
                        if self._texture_is_transparent[texture_path][1]:
                            check_faces = False
                        else:
                            opaque_face_count += 1

                    # get the texture
                    if texture_relative_path not in texture_dict:
                        texture_dict[texture_relative_path] = texture_count
                        textures.append(texture_path)
                        texture_count += 1

                    # texture index for the face
                    texture_index = texture_dict[texture_relative_path]

                    # get the uv values for each vertex
                    # TODO: get the uv based on box location if not defined
                    texture_uv = (
                        numpy.array(
                            element_faces[face_dir].get("uv", [0, 0, 16, 16]),
                            float,
                        )
                        / 16
                    )
                    texture_rotation = element_faces[face_dir].get("rotation", 0)
                    uv_slice = (
                        uv_rotation_lut[2 * int(texture_rotation / 90) :]
                        + uv_rotation_lut[: 2 * int(texture_rotation / 90)]
                    )

                    # merge the vertex coordinates and texture coordinates
                    face_verts = box_coordinates[cube_face_lut[face_dir]]
                    if "rotation" in element:
                        rotation = element["rotation"]
                        origin = [r / 16 for r in rotation.get("origin", [8, 8, 8])]
                        angle = rotation.get("angle", 0)
                        axis = rotation.get("axis", "x")
                        angles = [0, 0, 0]
                        if axis == "x":
                            angles[0] = -angle
                        elif axis == "y":
                            angles[1] = -angle
                        elif axis == "z":
                            angles[2] = -angle
                        face_verts = rotate_3d(face_verts, *angles, *origin)

                    verts_src[cull_dir].append(
                        face_verts
                    )  # vertex coordinates for this face

                    tverts_src[cull_dir].append(
                        texture_uv[uv_slice].reshape((-1, 2))  # texture vertices
                    )
                    if "tintindex" in element_faces[face_dir]:
                        tint_verts_src[cull_dir] += [
                            0,
                            1,
                            0,
                        ] * 4  # TODO: set this up for each supported block
                    else:
                        tint_verts_src[cull_dir] += [1, 1, 1] * 4

                    # merge the face indexes and texture index
                    face_table = tri_face + vert_count[cull_dir]
                    texture_indexes_src[cull_dir] += [texture_index, texture_index]

                    # faces stored under cull direction because this is the criteria to render them or not
                    faces_src[cull_dir].append(face_table)

                    vert_count[cull_dir] += 4

            if opaque_face_count == 6:
                transparent = Transparency.FullOpaque

        verts: dict[Optional[str], numpy.ndarray] = {}
        tverts: dict[Optional[str], numpy.ndarray] = {}
        tint_verts: dict[Optional[str], numpy.ndarray] = {}
        faces: dict[Optional[str], numpy.ndarray] = {}
        texture_indexes: dict[Optional[str], numpy.ndarray] = {}

        for cull_dir in FACE_KEYS:
            face_array = faces_src[cull_dir]
            if len(face_array) > 0:
                faces[cull_dir] = numpy.concatenate(face_array, axis=None)
                tint_verts[cull_dir] = numpy.concatenate(
                    tint_verts_src[cull_dir], axis=None
                )
                verts[cull_dir] = numpy.concatenate(verts_src[cull_dir], axis=None)
                tverts[cull_dir] = numpy.concatenate(tverts_src[cull_dir], axis=None)
                texture_indexes[cull_dir] = numpy.array(
                    texture_indexes_src[cull_dir], dtype=numpy.uint32
                )

        return BlockMesh(
            3,
            verts,
            tverts,
            tint_verts,
            faces,
            texture_indexes,
            tuple(textures),
            transparent,
        )

    def _recursive_load_block_model(self, model_path: str) -> dict:
        """Load a model json file and recursively load and merge the parent entries into one json file."""
        model_path_list = model_path.split(":", 1)
        if len(model_path_list) == 2:
            namespace, model_path = model_path_list
        else:
            namespace = "minecraft"
        if (namespace, model_path) in self._model_files:
            model = self._model_files[(namespace, model_path)]

            if "parent" in model:
                parent_model = self._recursive_load_block_model(model["parent"])
            else:
                parent_model = {}
            if "textures" in model:
                if "textures" not in parent_model:
                    parent_model["textures"] = {}
                for key, val in model["textures"].items():
                    parent_model["textures"][key] = val
            if "elements" in model:
                parent_model["elements"] = model["elements"]

            return parent_model

        return {}

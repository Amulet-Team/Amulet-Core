import os
import json
from typing import Union, Iterable, Iterator, Optional
from PIL import Image
import numpy
import glob
import itertools
import logging
import re

import amulet_nbt

from amulet.utils.cast import dynamic_cast
from amulet.block import Block
from amulet.resource_pack import BaseResourcePackManager
from amulet.resource_pack.java import JavaResourcePack
from amulet.mesh.block import (
    BlockMesh,
    BlockMeshPart,
    Triangle,
    Vertex,
    FloatVec3,
    FloatVec2,
    BlockMeshTransparency,
    BlockMeshCullDirection,
    merge_block_meshes,
    FACE_KEYS,
    CUBE_FACE_LUT,
    UV_ROTATION_LUT,
    TRI_FACE,
)
from amulet.mesh.util import rotate_3d

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

CULL_DIRECTIONS = {
    None: BlockMeshCullDirection.CullNone,
    "down": BlockMeshCullDirection.CullDown,
    "up": BlockMeshCullDirection.CullUp,
    "north": BlockMeshCullDirection.CullNorth,
    "east": BlockMeshCullDirection.CullEast,
    "south": BlockMeshCullDirection.CullSouth,
    "west": BlockMeshCullDirection.CullWest,
}


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
                            log.exception(
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
                                log.exception(
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
                                log.exception(
                                    f"Failed to load block model {case['apply']}\n{e}"
                                )
                    except Exception as e:
                        log.exception(f"Failed to parse block state for {block}\n{e}")

                return merge_block_meshes(models)

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

        model = self._load_block_model(model_path)

        # TODO: rotate model based on uv_lock
        return model.rotate(rotx, roty)

    def _load_block_model(self, model_path: str) -> BlockMesh:
        """Load the model file associated with the Block and convert to a BlockMesh."""
        # recursively load model files into one dictionary
        java_model = self._recursive_load_block_model(model_path)

        if java_model.get("textures", {}) and not java_model.get("elements"):
            return self.missing_block

        # set up some variables
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
        transparency = BlockMeshTransparency.Partial

        for element in dynamic_cast(java_model.get("elements", {}), dict):
            # iterate through elements (one cube per element)
            element_faces = dynamic_cast(element.get("faces", {}), dict)

            opaque_face_count = 0
            if (
                transparency
                and "rotation" not in element
                and element.get("to", [16, 16, 16]) == [16, 16, 16]
                and element.get("from", [0, 0, 0]) == [0, 0, 0]
                and len(element_faces) >= 6
            ):
                # if the block is not yet defined as a solid block
                # and this element is a full size element
                # check if the texture is opaque
                transparency = BlockMeshTransparency.FullTranslucent
                check_faces = True
            else:
                check_faces = False

            # lower and upper box coordinates
            x1, y1, z1 = [v / 16.0 for v in element.get("from", [0, 0, 0])]
            x2, y2, z2 = [v / 16.0 for v in element.get("to", [16, 16, 16])]

            # vertex coordinates of the box
            box_coordinates = numpy.array(
                list(
                    itertools.product(
                        (min(x1, x2), max(x1, x2)),
                        (min(y1, y2), max(y1, y2)),
                        (min(z1, z2), max(z1, x2)),
                    )
                )
            )

            for face_dir, face_data in element_faces.items():
                if face_dir not in CUBE_FACE_LUT:
                    continue

                # get the cull direction. If there is an opaque block in this direction then cull this face
                cull_dir = face_data.get("cullface", None)
                if cull_dir not in FACE_KEYS:
                    cull_dir = None

                # get the relative texture path for the texture used
                texture_relative_path = face_data.get("texture", None)
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

                texture_path = self.get_texture_path(namespace, texture_relative_path)

                if check_faces:
                    if self._texture_is_transparent[texture_path][1]:
                        check_faces = False
                    else:
                        opaque_face_count += 1

                # texture index for the face
                texture_index = texture_paths.setdefault(
                    texture_relative_path, len(texture_paths)
                )

                # get the uv values for each vertex
                texture_uv: tuple[float, float, float, float]
                if "uv" in face_data:
                    uv = face_data["uv"]
                    texture_uv = (
                        uv[0] / 16.0,
                        uv[1] / 16.0,
                        uv[2] / 16.0,
                        uv[3] / 16.0,
                    )
                else:
                    # TODO: get the uv based on box location if not defined
                    texture_uv = (0.0, 0.0, 1.0, 1.0)

                texture_rotation = face_data.get("rotation", 0)
                uv_slice = (
                    UV_ROTATION_LUT[2 * int(texture_rotation / 90) :]
                    + UV_ROTATION_LUT[: 2 * int(texture_rotation / 90)]
                )

                # merge the vertex coordinates and texture coordinates
                face_verts = box_coordinates[CUBE_FACE_LUT[face_dir]]
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

                cull_direction = CULL_DIRECTIONS[cull_dir]
                part = mesh_parts[cull_direction]
                if part is None:
                    mesh_parts[cull_direction] = part = ([], [])
                verts, tris = part
                vert_count = len(verts)

                if "tintindex" in face_data:
                    # TODO: set this up for each supported block
                    tint_vec = FloatVec3(0, 1, 0)
                else:
                    tint_vec = FloatVec3(1, 1, 1)

                for i in range(4):
                    x, y, z = face_verts[i]
                    uvx = texture_uv[uv_slice[i * 2]]
                    uvy = texture_uv[uv_slice[i * 2 + 1]]
                    verts.append(
                        Vertex(
                            FloatVec3(x, y, z),
                            FloatVec2(uvx, uvy),
                            tint_vec,
                        )
                    )

                for a, b, c in TRI_FACE.reshape((2, 3)):
                    tris.append(
                        Triangle(
                            a + vert_count,
                            b + vert_count,
                            c + vert_count,
                            texture_index,
                        )
                    )

            if opaque_face_count == 6:
                transparency = BlockMeshTransparency.FullOpaque

        def create_part(
            part: tuple[list[Vertex], list[Triangle]] | None
        ) -> BlockMeshPart | None:
            return None if part is None else BlockMeshPart(*part)

        return BlockMesh(
            transparency,
            list(texture_paths),
            (
                create_part(mesh_parts[0]),
                create_part(mesh_parts[1]),
                create_part(mesh_parts[2]),
                create_part(mesh_parts[3]),
                create_part(mesh_parts[4]),
                create_part(mesh_parts[5]),
                create_part(mesh_parts[6]),
            ),
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

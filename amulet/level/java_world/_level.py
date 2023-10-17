from __future__ import annotations

from typing import Any, Optional, Protocol, BinaryIO, Union, NamedTuple, Sequence
import os
import shutil
import time
import struct
import glob
import json
import logging

from PIL import Image
import portalocker
from amulet_nbt import (
    load as load_nbt,
    NamedTag,
    CompoundTag,
    IntTag,
    LongTag,
    StringTag,
    ListTag,
)

from amulet.api.data_types import (
    Dimension,
    BiomeType,
    VersionNumberInt,
    VersionNumberTuple,
)
from amulet.api.block import Block, UniversalAirBlock
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.level.base_level import (
    DiskLevel,
    CreatableLevel,
    CreateArgsT,
    StringArg,
    IntArg,
    SequenceArg,
    ProtocolArg,
    LoadableLevel,
    BaseLevelPrivate,
    CompactableLevel,
)
from amulet.utils.format_utils import check_all_exist

from ._dimension import AnvilDimensionManager
from ._data_pack import DataPackManager, DataPack

log = logging.getLogger(__name__)

InternalDimension = str
OVERWORLD = "minecraft:overworld"
THE_NETHER = "minecraft:the_nether"
THE_END = "minecraft:the_end"

DefaultSelection = SelectionGroup(
    SelectionBox((-30_000_000, 0, -30_000_000), (30_000_000, 256, 30_000_000))
)


# class DimensionData(Protocol):
#     name: Dimension
#     bounds: SelectionGroup
#     default_block: Block
#     default_biome: BiomeType


class DimensionEntry(NamedTuple):
    relative_dimension_path: InternalDimension
    dimension_name: Dimension
    manager: AnvilDimensionManager
    bounds: SelectionGroup
    default_block: Block
    default_biome: BiomeType


class JavaLevelPrivate(BaseLevelPrivate):
    __slots__ = (
        "path",
        "data_version",
        "root_tag",
        "mcc_support",
        "dimensions",
        "data_pack",
    )

    def __init__(self):
        super().__init__()
        self.path: Optional[str] = None
        self.data_version: Optional[VersionNumberInt] = None
        self.root_tag: Optional[NamedTag] = None
        self.mcc_support: bool = False
        self.dimensions: dict[Union[InternalDimension, Dimension], DimensionEntry] = {}
        self.data_pack: Optional[DataPackManager] = None


class JavaLevel(DiskLevel, CreatableLevel, LoadableLevel, CompactableLevel):
    __slots__ = (
        "_lock_file",
        "_lock_time",
    )
    _l: JavaLevelPrivate

    def __init__(self):
        super().__init__()
        self._lock_file: Optional[BinaryIO] = None
        self._lock_time: Optional[int] = None

    @staticmethod
    def _instance_data() -> JavaLevelPrivate:
        return JavaLevelPrivate()

    @classmethod
    def create(
        cls,
        *,
        path: str,
        name: str,
        version: VersionNumberTuple,
        # dimensions: Sequence[DimensionData],
        overwrite: bool = False,
        **kwargs,
    ) -> JavaLevel:
        if os.path.isdir(path):
            if overwrite:
                shutil.rmtree(path)
            else:
                raise ObjectWriteError(f"A world already exists at the path {path}")

        self = cls()
        self._l.path = path

        self._l.data_version = self.translator.get_version("java", version).data_version

        self.root_tag = root = CompoundTag()
        root["Data"] = data = CompoundTag()
        data["version"] = IntTag(19133)
        data["DataVersion"] = IntTag(self._l.data_version)
        data["LastPlayed"] = LongTag(int(time.time() * 1000))
        data["LevelName"] = StringTag(name)

        os.makedirs(self.path, exist_ok=True)
        self.root_tag.save_to(os.path.join(self.path, "level.dat"))

        return self

    @staticmethod
    def create_args() -> dict[str, CreateArgsT]:
        return {
            "path": StringArg(),
            "name": StringArg(),
            "version": SequenceArg(IntArg()),
            # "dimensions": SequenceArg(ProtocolArg(
            #
            # ))
        }

    @staticmethod
    def can_load(token: Any) -> bool:
        if (
            isinstance(token, str)
            and os.path.isdir(token)
            and check_all_exist(token, "level.dat")
        ):
            try:
                level_dat_root = load_nbt(os.path.join(token, "level.dat")).compound
            except Exception:
                pass
            else:
                return "Data" in level_dat_root and "FML" not in level_dat_root
        return False

    @classmethod
    def load(cls, path: str) -> JavaLevel:
        self = cls()
        self._l.path = path
        self._l.root_tag = load_nbt(os.path.join(self.path, "level.dat"))
        self._l.data_version = (
            self._l.root_tag.compound.get_compound("Data", CompoundTag())
            .get_int("DataVersion", IntTag(-1))
            .py_int
        )
        return self

    def _register_dimension(
        self,
        relative_dimension_path: InternalDimension,
        dimension_name: Optional[Dimension] = None,
    ):
        """
        Register a new dimension.

        :param relative_dimension_path: The relative path to the dimension directory from the world root.
            "" for the world root.
        :param dimension_name: The name of the dimension shown to the user
        """
        if dimension_name is None:
            dimension_name: Dimension = relative_dimension_path

        if relative_dimension_path:
            path = os.path.join(self.path, relative_dimension_path)
        else:
            path = self.path

        if (
            relative_dimension_path not in self._l.dimensions
            and dimension_name not in self._l.dimensions
        ):
            self._l.dimensions[relative_dimension_path] = self._l.dimensions[
                dimension_name
            ] = DimensionEntry(
                relative_dimension_path,
                dimension_name,
                AnvilDimensionManager(
                    path,
                    mcc=self._l.mcc_support,
                    layers=("region",) + ("entities",) * (self._l.data_version >= 2681),
                ),
                self._get_dimension_bounds(dimension_name),
                UniversalAirBlock,
                "universal_minecraft:plains",  # TODO: get this data from somewhere
            )

    def _get_dimension_bounds(self, dimension_type_str: Dimension) -> SelectionGroup:
        if self._l.data_version >= 2709:  # This number might be smaller
            # If in a version that supports custom height data packs
            dimension_settings = (
                self._l.root_tag.compound.get_compound("Data", CompoundTag())
                .get_compound("WorldGenSettings", CompoundTag())
                .get_compound("dimensions", CompoundTag())
                .get_compound(dimension_type_str, CompoundTag())
            )

            # "type" can be a reference (string) or inline (compound) dimension-type data.
            dimension_type = dimension_settings.get("type")

            if isinstance(dimension_type, StringTag):
                # Reference type. Load the dimension data
                dimension_type_str = dimension_type.py_str
                if ":" in dimension_type_str:
                    namespace, base_name = dimension_type_str.split(":", 1)
                else:
                    namespace = "minecraft"
                    base_name = dimension_type_str
                name_tuple = namespace, base_name

                # First try and load the reference from the data pack and then from defaults
                dimension_path = f"data/{namespace}/dimension_type/{base_name}.json"
                if self.data_pack.has_file(dimension_path):
                    with self.data_pack.open(dimension_path) as d:
                        try:
                            dimension_settings_json = json.load(d)
                        except json.JSONDecodeError:
                            pass
                        else:
                            if "min_y" in dimension_settings_json and isinstance(
                                dimension_settings_json["min_y"], int
                            ):
                                min_y = dimension_settings_json["min_y"]
                                if min_y % 16:
                                    min_y = 16 * (min_y // 16)
                            else:
                                min_y = 0
                            if "height" in dimension_settings_json and isinstance(
                                dimension_settings_json["height"], int
                            ):
                                height = dimension_settings_json["height"]
                                if height % 16:
                                    height = -16 * (-height // 16)
                            else:
                                height = 256

                            return SelectionGroup(
                                SelectionBox(
                                    (-30_000_000, min_y, -30_000_000),
                                    (30_000_000, min_y + height, 30_000_000),
                                )
                            )

                elif name_tuple in {
                    ("minecraft", "overworld"),
                    ("minecraft", "overworld_caves"),
                }:
                    if self._l.data_version >= 2825:
                        # If newer than the height change version
                        return SelectionGroup(
                            SelectionBox(
                                (-30_000_000, -64, -30_000_000),
                                (30_000_000, 320, 30_000_000),
                            )
                        )
                    else:
                        return DefaultSelection
                elif name_tuple in {
                    ("minecraft", "the_nether"),
                    ("minecraft", "the_end"),
                }:
                    return DefaultSelection
                else:
                    log.error(f"Could not find dimension_type {':'.join(name_tuple)}")

            elif isinstance(dimension_type, CompoundTag):
                # Inline type
                dimension_type_compound = dimension_type
                min_y = (
                    dimension_type_compound.get_int("min_y", IntTag()).py_int // 16
                ) * 16
                height = (
                    -dimension_type_compound.get_int("height", IntTag(256)).py_int // 16
                ) * -16
                return SelectionGroup(
                    SelectionBox(
                        (-30_000_000, min_y, -30_000_000),
                        (30_000_000, min_y + height, 30_000_000),
                    )
                )
            else:
                log.error(
                    f'level_dat["Data"]["WorldGenSettings"]["dimensions"]["{dimension_type_str}"]["type"] was not a StringTag or CompoundTag.'
                )

        # Return the default if nothing else returned
        return DefaultSelection

    def _open(self):
        # create the session.lock file
        try:
            # open the file for writing and reading and lock it
            self._lock_file = open(os.path.join(self.path, "session.lock"), "wb+")
            portalocker.lock(self._lock_file, portalocker.LockFlags.EXCLUSIVE)

            # write the current time to the file
            self._lock_time = struct.pack(">Q", int(time.time() * 1000))
            self._lock_file.write(self._lock_time)

            # flush the changes to disk
            self._lock_file.flush()
            os.fsync(self._lock_file.fileno())

        except Exception as e:
            self._lock_time = None
            if self._lock_file is not None:
                self._lock_file.close()
                self._lock_file = None

            raise Exception(
                f"Could not access session.lock. The world may be open somewhere else.\n{e}"
            ) from e

        self._l.mcc_support = self._l.data_version > 2203

        # load all the levels
        self._register_dimension("", OVERWORLD)
        self._register_dimension("DIM-1", THE_NETHER)
        self._register_dimension("DIM1", THE_END)

        for level_path in glob.glob(os.path.join(glob.escape(self.path), "DIM*")):
            if os.path.isdir(level_path):
                dir_name = os.path.basename(level_path)
                if AnvilDimensionManager.level_regex.fullmatch(dir_name) is None:
                    continue
                self._register_dimension(dir_name)

        for region_path in glob.glob(
            os.path.join(
                glob.escape(self.path), "dimensions", "*", "*", "**", "region"
            ),
            recursive=True,
        ):
            if not os.path.isdir(region_path):
                continue
            dimension_path = os.path.dirname(region_path)
            rel_dim_path = os.path.relpath(dimension_path, self.path)
            _, dimension, *base_name = rel_dim_path.split(os.sep)

            dimension_name = f"{dimension}:{'/'.join(base_name)}"
            self._register_dimension(rel_dim_path, dimension_name)

    def _close(self):
        self._l.dimensions.clear()
        if self._lock_file is not None:
            portalocker.unlock(self._lock_file)
            self._lock_file.close()

    @property
    def path(self) -> str:
        if self._l.path is None:
            raise RuntimeError
        return self._l.path

    @property
    def thumbnail(self) -> Image.Image:
        try:
            return Image.open(os.path.join(self.path, "icon.png"))
        except Exception:
            return super().thumbnail

    @property
    def data_pack(self) -> DataPackManager:
        if self._l.data_pack is None:
            packs = []
            enabled_packs = (
                self._l.root_tag.compound.get_compound("Data")
                .get_compound("DataPacks", CompoundTag())
                .get_list("Enabled", ListTag())
            )
            for pack in enabled_packs:
                if isinstance(pack, StringTag):
                    pack_name: str = pack.py_str
                    if pack_name == "vanilla":
                        pass
                    elif pack_name.startswith("file/"):
                        path = os.path.join(self.path, "datapacks", pack_name[5:])
                        if DataPack.is_path_valid(path):
                            packs.append(DataPack(path))
            self._l.data_pack = DataPackManager(packs)
        return self._l.data_pack

    @property
    def dimensions(self) -> Sequence[Dimension]:
        return tuple(filter(lambda e: isinstance(e, Dimension), self._l.dimensions))

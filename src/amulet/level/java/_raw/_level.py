from __future__ import annotations

from typing import BinaryIO, Callable
import copy
from threading import RLock
import logging
from dataclasses import dataclass
import shutil
import time
import glob
import json
import struct
import os

import portalocker

from amulet_nbt import (
    IntTag,
    LongTag,
    StringTag,
    ListTag,
    CompoundTag,
    read_nbt,
    NamedTag,
)

from amulet.data_types import DimensionId
from amulet.block import BlockStack, Block
from amulet.biome import Biome
from amulet.game import get_game_version
from amulet.selection import SelectionGroup, SelectionBox
from amulet.errors import LevelWriteError
from amulet.level.abc import (
    RawLevel,
    IdRegistry,
)
from amulet.version import VersionNumber
from amulet.utils.signal import Signal, SignalInstanceCacheName
from amulet.utils.weakref import DetachableWeakRef

from amulet.level.java.anvil import AnvilDimension
from ._data_pack import DataPackManager, DataPack
from ._dimension import JavaRawDimension
from ._typing import InternalDimensionId
from ._constant import OVERWORLD, THE_NETHER, THE_END, DefaultSelection


log = logging.getLogger(__name__)


@dataclass
class JavaCreateArgsV1:
    """A class to house call arguments to create.

    If the call arguments to create need to be modified in the future a new arguments class can be created.
    The create method can inspect which class it was given and access arguments accordingly.
    """

    overwrite: bool
    path: str
    version: VersionNumber
    level_name: str


class JavaRawLevelOpenData:
    back_reference: Callable[[], JavaRawLevel | None]
    detach_back_reference: Callable[[], None]
    lock_file: BinaryIO
    lock_time: float
    data_pack: DataPackManager
    dimensions: dict[InternalDimensionId, JavaRawDimension]
    dimension_ids: dict[DimensionId, InternalDimensionId]
    dimensions_lock: RLock
    block_id_override: IdRegistry
    biome_id_override: IdRegistry

    def __init__(
        self,
        raw_level: JavaRawLevel,
        lock_file: BinaryIO,
        lock_time: float,
        data_pack: DataPackManager,
    ) -> None:
        self.back_reference, self.detach_back_reference = DetachableWeakRef.new(
            raw_level
        )
        self.lock_file = lock_file
        self.lock_time = lock_time
        self.data_pack = data_pack
        self.dimensions = {}
        self.dimension_ids = {}
        self.dimensions_lock = RLock()
        self.block_id_override = IdRegistry()
        self.biome_id_override = IdRegistry()


class JavaRawLevel(RawLevel[JavaRawDimension]):
    _path: str
    _level_dat: NamedTag
    _data_version: VersionNumber
    _raw_open_data: JavaRawLevelOpenData | None

    __slots__ = (
        "_path",
        "_level_dat",
        "_data_version",
        "_raw_open_data",
        SignalInstanceCacheName,
    )

    def __init__(self, _ikwiad: bool = False) -> None:
        if not _ikwiad:
            raise RuntimeError(
                "JavaRawLevel must be constructed using the create or load classmethod."
            )

    @classmethod
    def load(cls, path: str) -> JavaRawLevel:
        self = cls(True)
        self._path = path
        self._raw_open_data = None
        self.reload()
        return self

    @classmethod
    def create(cls, args: JavaCreateArgsV1) -> JavaRawLevel:
        overwrite = args.overwrite
        path = args.path
        version = args.version
        level_name = args.level_name

        if os.path.isdir(path):
            if overwrite:
                shutil.rmtree(path)
            else:
                raise LevelWriteError(f"A world already exists at the path {path}")
        os.makedirs(path, exist_ok=True)

        data_version = get_game_version("java", version).max_version

        root = CompoundTag()
        root["Data"] = data = CompoundTag()
        data["version"] = IntTag(19133)
        data["DataVersion"] = IntTag(data_version[0])
        data["LastPlayed"] = LongTag(int(time.time() * 1000))
        data["LevelName"] = StringTag(level_name)

        root.save_to(os.path.join(path, "level.dat"))

        return cls.load(path)

    def is_open(self) -> bool:
        return self._raw_open_data is not None

    @property
    def _o(self) -> JavaRawLevelOpenData:
        o = self._raw_open_data
        if o is None:
            raise RuntimeError("The level is not open.")
        return o

    def _update_data_version(self) -> None:
        """Pull the data version from the level.dat file"""
        self._data_version = VersionNumber(
            self._level_dat.compound.get_compound("Data", CompoundTag())
            .get_int("DataVersion", IntTag(-1))
            .py_int
        )

    def reload(self) -> None:
        """Reload the raw level."""
        if self.is_open():
            raise RuntimeError("Cannot reload a level when it is open.")
        self._level_dat = read_nbt(os.path.join(self.path, "level.dat"))
        self._update_data_version()

    opened = Signal[()]()

    def open(self) -> None:
        """Open the raw level."""
        if self.is_open():
            return

        # create the session.lock file
        try:
            # Try to open the file
            lock = portalocker.Lock(
                os.path.join(self.path, "session.lock"),
                "wb+",
                fail_when_locked=True,
            )
            lock_file: BinaryIO = lock.acquire()  # type: ignore
        except portalocker.LockException:
            raise Exception(
                f"Could not acquire session.lock. The world may be open somewhere else."
            )
        else:
            # write the current time to the file
            lock_time = time.time()
            lock_file.write(struct.pack(">Q", int(lock_time * 1000)))

            # flush the changes to disk
            lock_file.flush()
            os.fsync(lock_file.fileno())

        packs = []
        enabled_packs = (
            self.level_dat.compound.get_compound("Data", CompoundTag())
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
        data_pack = DataPackManager(packs)

        self._raw_open_data = JavaRawLevelOpenData(
            self, lock_file, lock_time, data_pack
        )
        self.opened.emit()

    closed = Signal[()]()

    def close(self) -> None:
        """Close the raw level."""
        if not self.is_open():
            return
        open_data = self._o
        portalocker.unlock(open_data.lock_file)
        open_data.lock_file.close()
        open_data.detach_back_reference()
        self._raw_open_data = None
        self.closed.emit()

    @property
    def path(self) -> str:
        return self._path

    @property
    def level_dat(self) -> NamedTag:
        """Get the level.dat file for the world"""
        return copy.deepcopy(self._level_dat)

    @level_dat.setter
    def level_dat(self, level_dat: NamedTag) -> None:
        if not isinstance(level_dat, NamedTag):
            raise TypeError
        if not self.is_open():
            raise RuntimeError("Level is not open.")
        self._level_dat = level_dat = copy.deepcopy(level_dat)
        self._update_data_version()
        level_dat.save_to(os.path.join(self.path, "level.dat"))

    @property
    def platform(self) -> str:
        return "java"

    @property
    def data_version(self) -> VersionNumber:
        """
        The game data version that the level was last opened in.
        This is used to determine the data format to save in.
        """
        return self._data_version

    @property
    def modified_time(self) -> float:
        """Unix timestamp of when the level was last modified."""
        return (
            self.level_dat.compound.get_compound("Data", CompoundTag())
            .get_long("LastPlayed", LongTag())
            .py_int
            / 1000
        )

    @property
    def level_name(self) -> str:
        return (
            self._level_dat.compound.get_compound("Data", CompoundTag())
            .get_string("LevelName", StringTag("Undefined"))
            .py_str
        )

    @level_name.setter
    def level_name(self, value: str) -> None:
        level_dat = self.level_dat
        level_dat.compound.setdefault_compound("Data")["LevelName"] = StringTag(value)
        self.level_dat = level_dat

    def _get_dimension_bounds(self, dimension_type_str: DimensionId) -> SelectionGroup:
        if self._data_version >= VersionNumber(2709):  # This number might be smaller
            # If in a version that supports custom height data packs
            dimension_settings = (
                self.level_dat.compound.get_compound("Data", CompoundTag())
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
                if self._o.data_pack.has_file(dimension_path):
                    with self._o.data_pack.open(dimension_path) as d:
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
                    if self.data_version >= VersionNumber(2825):
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

    def _register_dimension(
        self,
        relative_dimension_path: InternalDimensionId,
        dimension_name: DimensionId,
    ) -> None:
        """
        Register a new dimension.

        :param relative_dimension_path: The relative path to the dimension directory from the world root.
            "" for the world root.
        :param dimension_name: The name of the dimension shown to the user
        """
        if relative_dimension_path:
            path = os.path.join(self.path, relative_dimension_path)
        else:
            path = self.path

        if (
            relative_dimension_path not in self._o.dimensions
            and dimension_name not in self._o.dimension_ids
        ):
            self._o.dimension_ids[dimension_name] = relative_dimension_path
            self._o.dimensions[relative_dimension_path] = JavaRawDimension(
                self._o.back_reference,
                # TODO: The data version can change while the level is open.
                #  That may cause problems with this.
                AnvilDimension(
                    path,
                    mcc=self.data_version > VersionNumber(2203),
                    layers=("region",)
                    + ("entities",) * (self.data_version >= VersionNumber(2681)),
                ),
                relative_dimension_path,
                dimension_name,
                self._get_dimension_bounds(dimension_name),
                # TODO: Is this data stored somewhere?
                BlockStack(Block("java", VersionNumber(3700), "minecraft", "air")),
                (
                    Biome("java", VersionNumber(3700), "minecraft", "nether_wastes")
                    if dimension_name == THE_NETHER
                    else (
                        Biome("java", VersionNumber(3700), "minecraft", "the_end")
                        if dimension_name == THE_END
                        else Biome("java", VersionNumber(3700), "minecraft", "plains")
                    )
                ),
            )

    def _find_dimensions(self) -> None:
        with self._o.dimensions_lock:
            if self._o.dimensions:
                return

            # load all the levels
            self._register_dimension("", OVERWORLD)
            self._register_dimension("DIM-1", THE_NETHER)
            self._register_dimension("DIM1", THE_END)

            for level_path in glob.glob(os.path.join(glob.escape(self.path), "DIM*")):
                if os.path.isdir(level_path):
                    dir_name = os.path.basename(level_path)
                    if AnvilDimension.level_regex.fullmatch(dir_name) is None:
                        continue
                    self._register_dimension(dir_name, dir_name)

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

    def dimension_ids(self) -> frozenset[DimensionId]:
        self._find_dimensions()
        return frozenset(self._o.dimension_ids)

    def get_dimension(self, dimension_id: DimensionId) -> JavaRawDimension:
        self._find_dimensions()
        internal_dimension_id = self._o.dimension_ids.get(dimension_id, dimension_id)
        if internal_dimension_id not in self._o.dimensions:
            raise RuntimeError(f"Dimension {dimension_id} does not exist")
        return self._o.dimensions[internal_dimension_id]

    def compact(self) -> None:
        """Compact all region files"""
        for dimension_id in self.dimension_ids():
            self.get_dimension(dimension_id).compact()

    @property
    def block_id_override(self) -> IdRegistry:
        """
        A two-way map from hard coded numerical block id <-> block string.
        This only stores overridden values. If the value is not present here you should check the translator.
        """
        return self._o.block_id_override

    @property
    def biome_id_override(self) -> IdRegistry:
        """
        A two-way map from hard coded numerical biome id <-> biome string.
        This only stores overridden values. If the value is not present here you should check the translator.
        """
        return self._o.biome_id_override

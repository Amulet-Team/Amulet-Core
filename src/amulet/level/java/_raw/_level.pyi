from __future__ import annotations

import copy as copy
import glob as glob
import json as json
import logging as logging
import os as os
import shutil as shutil
import struct as struct
import time as time
import typing
from builtins import str as DimensionId
from builtins import str as InternalDimensionId
from dataclasses import dataclass
from threading import RLock
from typing import BinaryIO

import amulet.level.abc._raw_level
import amulet.selection.group
import portalocker as portalocker
from amulet.biome import Biome
from amulet.block import Block, BlockStack
from amulet.errors import LevelWriteError
from amulet.game._game import get_game_version
from amulet.level.abc._raw_level import RawLevel
from amulet.level.abc._registry import IdRegistry
from amulet.level.java._raw._data_pack.data_pack import DataPack
from amulet.level.java._raw._data_pack.data_pack_manager import DataPackManager
from amulet.level.java._raw._dimension import JavaRawDimension
from amulet.level.java.anvil._dimension import AnvilDimension
from amulet.selection.box import SelectionBox
from amulet.selection.group import SelectionGroup
from amulet.utils.signal._signal import Signal
from amulet.utils.weakref import DetachableWeakRef
from amulet.version import VersionNumber
from amulet_nbt import (
    CompoundTag,
    IntTag,
    ListTag,
    LongTag,
    NamedTag,
    StringTag,
    read_nbt,
)

__all__ = [
    "AnvilDimension",
    "BinaryIO",
    "Biome",
    "Block",
    "BlockStack",
    "CompoundTag",
    "DataPack",
    "DataPackManager",
    "DefaultSelection",
    "DetachableWeakRef",
    "DimensionId",
    "IdRegistry",
    "IntTag",
    "InternalDimensionId",
    "JavaCreateArgsV1",
    "JavaRawDimension",
    "JavaRawLevel",
    "JavaRawLevelOpenData",
    "LevelWriteError",
    "ListTag",
    "LongTag",
    "NamedTag",
    "OVERWORLD",
    "RLock",
    "RawLevel",
    "SelectionBox",
    "SelectionGroup",
    "Signal",
    "SignalInstanceCacheName",
    "StringTag",
    "THE_END",
    "THE_NETHER",
    "VersionNumber",
    "copy",
    "dataclass",
    "get_game_version",
    "glob",
    "json",
    "log",
    "logging",
    "os",
    "portalocker",
    "read_nbt",
    "shutil",
    "struct",
    "time",
]

class JavaCreateArgsV1:
    """
    A class to house call arguments to create.

        If the call arguments to create need to be modified in the future a new arguments class can be created.
        The create method can inspect which class it was given and access arguments accordingly.

    """

    __hash__: typing.ClassVar[None] = None
    def __eq__(self, other): ...
    def __init__(
        self, overwrite: bool, path: str, version: VersionNumber, level_name: str
    ) -> None: ...
    def __repr__(self): ...

class JavaRawLevel(amulet.level.abc._raw_level.RawLevel):
    __slots__: typing.ClassVar[tuple] = (
        "_path",
        "_level_dat",
        "_data_version",
        "_raw_open_data",
        "_SignalCache",
    )
    level_name: str
    @staticmethod
    def closed(*args, **kwargs): ...
    @staticmethod
    def opened(*args, **kwargs): ...
    @classmethod
    def create(cls, args: JavaCreateArgsV1) -> JavaRawLevel: ...
    @classmethod
    def load(cls, path: str) -> JavaRawLevel: ...
    def __init__(self, _ikwiad: bool = False) -> None: ...
    def _find_dimensions(self) -> None: ...
    def _get_dimension_bounds(
        self, dimension_type_str: DimensionId
    ) -> SelectionGroup: ...
    def _register_dimension(
        self, relative_dimension_path: InternalDimensionId, dimension_name: DimensionId
    ) -> None:
        """

        Register a new dimension.

        :param relative_dimension_path: The relative path to the dimension directory from the world root.
            "" for the world root.
        :param dimension_name: The name of the dimension shown to the user

        """

    def _update_data_version(self) -> None:
        """
        Pull the data version from the level.dat file
        """

    def close(self) -> None:
        """
        Close the raw level.
        """

    def compact(self) -> None:
        """
        Compact all region files
        """

    def dimension_ids(self) -> frozenset[DimensionId]: ...
    def get_dimension(self, dimension_id: DimensionId) -> JavaRawDimension: ...
    def is_open(self) -> bool: ...
    def open(self) -> None:
        """
        Open the raw level.
        """

    def reload(self) -> None:
        """
        Reload the raw level.
        """

    @property
    def _o(self) -> JavaRawLevelOpenData: ...
    @property
    def biome_id_override(self) -> IdRegistry:
        """

        A two-way map from hard coded numerical biome id <-> biome string.
        This only stores overridden values. If the value is not present here you should check the translator.

        """

    @property
    def block_id_override(self) -> IdRegistry:
        """

        A two-way map from hard coded numerical block id <-> block string.
        This only stores overridden values. If the value is not present here you should check the translator.

        """

    @property
    def data_version(self) -> VersionNumber:
        """

        The game data version that the level was last opened in.
        This is used to determine the data format to save in.

        """

    @property
    def level_dat(self) -> NamedTag:
        """
        Get the level.dat file for the world
        """

    @level_dat.setter
    def level_dat(self, level_dat: NamedTag) -> None: ...
    @property
    def modified_time(self) -> float:
        """
        Unix timestamp of when the level was last modified.
        """

    @property
    def path(self) -> str: ...
    @property
    def platform(self) -> str: ...

class JavaRawLevelOpenData:
    def __init__(
        self,
        raw_level: JavaRawLevel,
        lock_file: BinaryIO,
        lock_time: float,
        data_pack: DataPackManager,
    ) -> None: ...

DefaultSelection: (
    amulet.selection.group.SelectionGroup
)  # value = SelectionGroup([SelectionBox((-30000000, 0, -30000000), (30000000, 256, 30000000))])
OVERWORLD: str
SignalInstanceCacheName: str
THE_END: str
THE_NETHER: str
log: logging.Logger  # value = <Logger amulet.level.java._raw._level (INFO)>

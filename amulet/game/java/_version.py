from __future__ import annotations
from typing import Self
import os
import json

from amulet.game import get_game_version
from amulet.game.abc import GameVersion, BiomeData, load_json_block_spec
from amulet.game.abc.translate import (
    BlockToUniversalTranslator,
    BlockFromUniversalTranslator,
    load_json_block_translations,
)
from amulet.version import VersionNumber

from ._block import JavaBlockData, Waterloggable


class JavaGameVersion(GameVersion):
    _block: JavaBlockData

    def __init__(
        self,
        min_data_version: VersionNumber,
        max_data_version: VersionNumber,
        min_semantic_version: VersionNumber,
        max_semantic_version: VersionNumber,
    ):
        """Do not use this."""
        self._min_data_version = min_data_version
        self._max_data_version = max_data_version
        self._min_semantic_version = min_semantic_version
        self._max_semantic_version = max_semantic_version

    def supports_version(self, platform: str, version: VersionNumber) -> bool:
        return platform == "java" and (
            self._min_data_version <= version <= self._max_data_version
            or self._min_semantic_version <= version <= self._max_semantic_version
        )

    @property
    def platform(self) -> str:
        return "java"

    @property
    def min_version(self) -> VersionNumber:
        return self._min_data_version

    @property
    def max_version(self) -> VersionNumber:
        return self._max_data_version

    @property
    def block(self) -> JavaBlockData:
        return self._block

    @property
    def biome(self) -> BiomeData:
        raise NotImplementedError

    @classmethod
    def from_json(cls, version_path: str) -> Self:
        with open(os.path.join(version_path, "__init__.json")) as f:
            init = json.load(f)
        assert init["platform"] == "java"
        min_data_version = VersionNumber(init["data_version"])
        max_data_version = VersionNumber(init["data_version"])  # TODO: Add max field
        min_semantic_version = VersionNumber(init["version"])
        max_semantic_version = VersionNumber(init["version"])  # TODO: Add max field

        block_format = init["block_format"]
        universal_version = get_game_version("universal", VersionNumber(1))

        self = cls(
            min_data_version,
            max_data_version,
            min_semantic_version,
            max_semantic_version,
        )

        # Load the block specification and translations
        block_spec = load_json_block_spec(version_path, block_format)
        block_to_universal = load_json_block_translations(
            version_path,
            block_format,
            "to_universal",
            BlockToUniversalTranslator,
            lambda namespace, base_name: block_spec[namespace][base_name],
            universal_version
        )
        block_from_universal = load_json_block_translations(
            version_path,
            block_format,
            "from_universal",
            BlockFromUniversalTranslator,
            universal_version.block.get_specification,
            self
        )

        waterloggable = dict[tuple[str, str], Waterloggable]()
        for name, state in (
            ("__waterloggable__.json", Waterloggable.Yes),
            ("__always_waterlogged__.json", Waterloggable.Always),
        ):
            file_path = os.path.join(version_path, name)
            if not os.path.isfile(file_path):
                continue
            with open(file_path) as f:
                blocks: list[str] = json.load(f)
            for block in blocks:
                namespace, base_name = block.split(":", 1)
                waterloggable[(namespace, base_name)] = state

        numerical_block_map = {}
        file_path = os.path.join(version_path, "__numerical_block_map__.json")
        if os.path.isfile(file_path):
            with open(file_path) as f:
                block_map: dict[str, int] = json.load(f)
            for block_str, block_num in block_map.items():
                namespace, base_name = block_str.split(":", 1)
                numerical_block_map[block_num] = (namespace, base_name)

        self._block = JavaBlockData(
            self,
            block_spec,
            block_to_universal,
            block_from_universal,
            numerical_block_map,
            waterloggable
        )

        return self

from __future__ import annotations
from typing import Self
import json
import os

from amulet.biome import Biome
from amulet.game import get_game_version
from amulet.game.abc import GameVersion, load_json_block_spec, load_json_biome_data
from amulet.game.translate import (
    BlockToUniversalTranslator,
    BlockFromUniversalTranslator,
    load_json_block_translations,
)
from amulet.version import VersionNumber

from ._block import BedrockBlockData
from ._biome import BedrockBiomeData


class BedrockGameVersion(GameVersion):
    _block: BedrockBlockData
    _biome: BedrockBiomeData

    def __init__(
        self,
        min_data_version: VersionNumber,
        max_data_version: VersionNumber,
        min_semantic_version: VersionNumber,
        max_semantic_version: VersionNumber,
    ) -> None:
        """Do not use this."""
        self._min_data_version = min_data_version
        self._max_data_version = max_data_version
        self._min_semantic_version = min_semantic_version
        self._max_semantic_version = max_semantic_version

    def supports_version(self, platform: str, version: VersionNumber) -> bool:
        return platform == "bedrock" and (
            self._min_data_version <= version <= self._max_data_version
            or self._min_semantic_version <= version <= self._max_semantic_version
        )

    @classmethod
    def from_json(cls, version_path: str) -> Self:
        with open(os.path.join(version_path, "__init__.json")) as f:
            init = json.load(f)
        assert init["platform"] == "bedrock"
        min_data_version = VersionNumber(init.get("data_version", -1))
        max_data_version = VersionNumber(init.get("data_version_max", -1))
        min_semantic_version = VersionNumber(*init["version"])
        max_semantic_version = VersionNumber(*init["version_max"])

        block_format = {
            "numerical": "numerical",
            "pseudo-numerical": "numerical",
            "nbt-blockstate": "blockstate",
        }[init["block_format"]]
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
            universal_version,
        )
        block_from_universal = load_json_block_translations(
            version_path,
            block_format,
            "from_universal",
            BlockFromUniversalTranslator,
            universal_version.block.get_specification,
            self,
        )

        numerical_block_map = {}
        file_path = os.path.join(version_path, "__numerical_block_map__.json")
        if os.path.isfile(file_path):
            with open(file_path) as f:
                block_map: dict[str, int] = json.load(f)
            for block_str, block_num in block_map.items():
                namespace, base_name = block_str.split(":", 1)
                numerical_block_map[block_num] = (namespace, base_name)

        self._block = BedrockBlockData(
            self,
            block_spec,
            block_to_universal,
            block_from_universal,
            numerical_block_map,
        )

        biomes, to_universal, from_universal = load_json_biome_data(version_path)
        biome_namespace = dict[str, list[str]]()
        for namespace, base_name in biomes:
            biome_namespace.setdefault(namespace, []).append(base_name)

        self._biome = BedrockBiomeData(
            self,
            biome_namespace,
            {
                biome: Biome(
                    "universal",
                    VersionNumber(1),
                    universal_namespace,
                    universal_base_name,
                )
                for (
                    biome,
                    (universal_namespace, universal_base_name),
                ) in to_universal.items()
            },
            {
                Biome(
                    "universal",
                    VersionNumber(1),
                    universal_namespace,
                    universal_base_name,
                ): biome
                for (
                    (universal_namespace, universal_base_name),
                    biome,
                ) in from_universal.items()
            },
            {
                biome_id: biome
                for biome, biome_id in biomes.items()
                if biome_id is not None
            },
        )

        return self

    def __repr__(self) -> str:
        return f"BedrockGameVersion({self.min_version!r})"

    @property
    def platform(self) -> str:
        return "bedrock"

    @property
    def min_version(self) -> VersionNumber:
        return self._min_semantic_version

    @property
    def max_version(self) -> VersionNumber:
        return self._max_semantic_version

    @property
    def block(self) -> BedrockBlockData:
        return self._block

    @property
    def biome(self) -> BedrockBiomeData:
        return self._biome

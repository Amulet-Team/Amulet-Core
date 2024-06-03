from __future__ import annotations
from typing import Self
import os
import json

from amulet.game.abc import GameVersion, load_json_block_spec, load_json_biome_data
from amulet.version import VersionNumber

from ._block import UniversalBlockData
from ._biome import UniversalBiomeData


class UniversalVersion(GameVersion):
    _block: UniversalBlockData
    _biome: UniversalBiomeData

    @classmethod
    def from_json(cls, version_path: str) -> Self:
        with open(os.path.join(version_path, "__init__.json")) as f:
            init = json.load(f)
        assert init["platform"] == "universal"

        block_format = init["block_format"]

        self = cls()

        # Load the block specification and translations
        block_spec = load_json_block_spec(version_path, block_format)

        self._block = UniversalBlockData(
            self,
            block_spec,
        )

        biomes, _, _ = load_json_biome_data(version_path)
        biomes_namespace = dict[str, list[str]]()
        for namespace, base_name in biomes:
            biomes_namespace.setdefault(namespace, []).append(base_name)

        self._biome = UniversalBiomeData(self, biomes_namespace)

        return self

    def __repr__(self) -> str:
        return f"UniversalVersion()"

    def supports_version(self, platform: str, version: VersionNumber) -> bool:
        return platform == "universal"

    @property
    def platform(self) -> str:
        return "universal"

    @property
    def min_version(self) -> VersionNumber:
        return VersionNumber(1)

    @property
    def max_version(self) -> VersionNumber:
        return VersionNumber(1)

    @property
    def block(self) -> UniversalBlockData:
        return self._block

    @property
    def biome(self) -> UniversalBiomeData:
        return self._biome

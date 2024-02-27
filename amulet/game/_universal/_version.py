from __future__ import annotations
from typing import Self, Any
import os
import json

from amulet.game.abc import GameVersion, BiomeData, load_json_block_spec
from amulet.version import VersionNumber

from ._block import UniversalBlockData


class UniversalVersion(GameVersion):
    _block: UniversalBlockData

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

        return self

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
    def biome(self) -> BiomeData:
        raise NotImplementedError

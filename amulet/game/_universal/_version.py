from __future__ import annotations

from amulet.game.abc import GameVersion, BiomeData, BlockData
from amulet.version import VersionNumber


class UniversalVersion(GameVersion):
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
    def block(self) -> BlockData:
        pass

    @property
    def biome(self) -> BiomeData:
        pass

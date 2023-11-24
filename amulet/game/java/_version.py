from __future__ import annotations

from amulet.game.abc import GameVersion, BiomeData
from amulet.version import VersionNumber
from ._block import JavaBlockData


class JavaGameVersion(GameVersion):
    def __init__(self) -> None:
        self._min_data_version: VersionNumber = VersionNumber()
        self._max_data_version: VersionNumber = VersionNumber()
        self._min_semantic_version: VersionNumber = VersionNumber()
        self._max_semantic_version: VersionNumber = VersionNumber()

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
        pass

    @property
    def biome(self) -> BiomeData:
        pass
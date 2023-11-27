from __future__ import annotations

from amulet.game.abc import GameVersion, BiomeData
from amulet.version import VersionNumber
from ._block import BedrockBlockData


class BedrockGameVersion(GameVersion):
    def __init__(
        self,
        min_semantic_version: VersionNumber,
        max_semantic_version: VersionNumber,
        block_data: BedrockBlockData,
    ) -> None:
        self._min_semantic_version = min_semantic_version
        self._max_semantic_version = max_semantic_version
        self._block_data = block_data

    def supports_version(self, platform: str, version: VersionNumber) -> bool:
        return (
            platform == "java"
            and self._min_semantic_version <= version <= self._max_semantic_version
        )

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
        return self._block_data

    @property
    def biome(self) -> BiomeData:
        pass

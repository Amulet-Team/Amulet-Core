from amulet.biome import Biome
from amulet.game.abc import BiomeData
from amulet.version import VersionNumber


class UniversalBiomeData(BiomeData):
    def to_universal(self, biome: Biome) -> Biome:
        if not self._game_version.supports_version(biome.platform, biome.version):
            raise ValueError("The block is not compatible with this version")
        return biome

    def from_universal(
        self, target_platform: str, target_version: VersionNumber, biome: Biome
    ) -> Biome:
        if not self._game_version.supports_version(biome.platform, biome.version):
            raise ValueError("The block is not compatible with this version")
        return biome

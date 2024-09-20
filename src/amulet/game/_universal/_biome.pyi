from amulet.biome import Biome as Biome
from amulet.game.abc import BiomeData as BiomeData
from amulet.version import VersionNumber as VersionNumber

class UniversalBiomeData(BiomeData):
    def to_universal(self, biome: Biome) -> Biome: ...
    def from_universal(
        self, target_platform: str, target_version: VersionNumber, biome: Biome
    ) -> Biome: ...

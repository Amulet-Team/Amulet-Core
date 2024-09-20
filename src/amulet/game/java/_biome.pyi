from collections.abc import Collection, Mapping

from amulet.biome import Biome as Biome
from amulet.game.abc import BiomeDataNumericalComponent as BiomeDataNumericalComponent
from amulet.game.abc import DatabaseBiomeData as DatabaseBiomeData
from amulet.game.abc import GameVersion as GameVersion

class JavaBiomeData(DatabaseBiomeData, BiomeDataNumericalComponent):
    def __init__(
        self,
        game_version: GameVersion,
        biomes: Mapping[str, Collection[str]],
        to_universal: Mapping[tuple[str, str], Biome],
        from_universal: Mapping[Biome, tuple[str, str]],
        numerical_map: Mapping[int, tuple[str, str]],
    ) -> None: ...
    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]: ...
    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int: ...

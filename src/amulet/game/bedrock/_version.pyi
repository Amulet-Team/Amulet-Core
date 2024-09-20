from typing import Self

from amulet.biome import Biome as Biome
from amulet.game import get_game_version as get_game_version
from amulet.game.abc import GameVersion as GameVersion
from amulet.game.abc import load_json_biome_data as load_json_biome_data
from amulet.game.abc import load_json_block_spec as load_json_block_spec
from amulet.game.translate import (
    BlockFromUniversalTranslator as BlockFromUniversalTranslator,
)
from amulet.game.translate import (
    BlockToUniversalTranslator as BlockToUniversalTranslator,
)
from amulet.game.translate import (
    load_json_block_translations as load_json_block_translations,
)
from amulet.version import VersionNumber as VersionNumber

from ._biome import BedrockBiomeData as BedrockBiomeData
from ._block import BedrockBlockData as BedrockBlockData

class BedrockGameVersion(GameVersion):
    def __init__(
        self,
        min_data_version: VersionNumber,
        max_data_version: VersionNumber,
        min_semantic_version: VersionNumber,
        max_semantic_version: VersionNumber,
    ) -> None:
        """Do not use this."""

    def supports_version(self, platform: str, version: VersionNumber) -> bool: ...
    @classmethod
    def from_json(cls, version_path: str) -> Self: ...
    @property
    def platform(self) -> str: ...
    @property
    def min_version(self) -> VersionNumber: ...
    @property
    def max_version(self) -> VersionNumber: ...
    @property
    def block(self) -> BedrockBlockData: ...
    @property
    def biome(self) -> BedrockBiomeData: ...

from typing import Self

from amulet.game.abc import GameVersion as GameVersion
from amulet.game.abc import load_json_biome_data as load_json_biome_data
from amulet.game.abc import load_json_block_spec as load_json_block_spec
from amulet.version import VersionNumber as VersionNumber

from ._biome import UniversalBiomeData as UniversalBiomeData
from ._block import UniversalBlockData as UniversalBlockData

class UniversalVersion(GameVersion):
    @classmethod
    def from_json(cls, version_path: str) -> Self: ...
    def supports_version(self, platform: str, version: VersionNumber) -> bool: ...
    @property
    def platform(self) -> str: ...
    @property
    def min_version(self) -> VersionNumber: ...
    @property
    def max_version(self) -> VersionNumber: ...
    @property
    def block(self) -> UniversalBlockData: ...
    @property
    def biome(self) -> UniversalBiomeData: ...

import abc
from abc import ABC, abstractmethod
from collections.abc import Collection, Mapping

from amulet.biome import Biome as Biome
from amulet.game import get_game_version as get_game_version
from amulet.version import VersionNumber as VersionNumber

from .game_version_container import GameVersionContainer as GameVersionContainer
from .version import GameVersion as GameVersion

class BiomeTranslationError(Exception):
    """An exception raised if the biome could not be translated."""

class BiomeData(GameVersionContainer, ABC, metaclass=abc.ABCMeta):
    def __init__(
        self, game_version: GameVersion, biomes: Mapping[str, Collection[str]]
    ) -> None: ...
    def namespaces(self) -> Collection[str]:
        """An iterable of all the valid biome namespaces."""

    def base_names(self, namespace: str) -> Collection[str]:
        """An iterable of all valid base names for the given namespace."""

    def translate(
        self, target_platform: str, target_version: VersionNumber, biome: Biome
    ) -> Biome:
        """Translate a biome from this version to the target version specified.

        :param target_platform: The game platform to convert to.
        :param target_version: The game version number to convert to.
        :param biome: The biome to translate.
        :return: The biome converted to the output version.
        :raises:
            ValueError: The arguments are incorrect. You did something wrong.
            BlockTranslationError: The translator is not aware of the biome. You should handle a sensible default.
        """

    @abstractmethod
    def to_universal(self, biome: Biome) -> Biome:
        """Convert a biome to the universal format.

        This method should be considered private.

        :meta private:
        :param biome: The biome to translate.
        :return: The biome converted to the universal version.
        :raises:
            ValueError: The arguments are incorrect. You did something wrong.
            BlockTranslationError: The translator is not aware of the biome. You should handle a sensible default.
        """

    @abstractmethod
    def from_universal(
        self, target_platform: str, target_version: VersionNumber, biome: Biome
    ) -> Biome:
        """Convert a biome from the universal format.

        This method should be considered private.

        :meta private:
        :param target_platform: The game platform to convert to.
        :param target_version: The game version number to convert to.
        :param biome: The biome to translate.
        :return: The biome converted to this version.
        :raises:
            ValueError: The arguments are incorrect. You did something wrong.
            BlockTranslationError: The translator is not aware of the biome. You should handle a sensible default.
        """

class DatabaseBiomeData(BiomeData):
    def __init__(
        self,
        game_version: GameVersion,
        biomes: Mapping[str, Collection[str]],
        to_universal: Mapping[tuple[str, str], Biome],
        from_universal: Mapping[Biome, tuple[str, str]],
    ) -> None: ...
    def to_universal(self, biome: Biome) -> Biome: ...
    def from_universal(
        self, target_platform: str, target_version: VersionNumber, biome: Biome
    ) -> Biome: ...

class BiomeDataNumericalComponent(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]:
        """Convert the numerical id to its namespace id"""

    @abstractmethod
    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int: ...

def load_json_biome_data(
    version_path: str,
) -> tuple[
    dict[tuple[str, str], int | None],
    dict[tuple[str, str], tuple[str, str]],
    dict[tuple[str, str], tuple[str, str]],
]: ...

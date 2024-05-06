from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from collections.abc import Mapping, Collection
import os
import json

from amulet.biome import Biome
from amulet.version import VersionNumber
from amulet.game import get_game_version

from .game_version_container import GameVersionContainer


if TYPE_CHECKING:
    from .version import GameVersion


class BiomeTranslationError(Exception):
    """An exception raised if the biome could not be translated."""


class BiomeData(GameVersionContainer, ABC):
    _biomes: Mapping[str, Collection[str]]

    def __init__(
        self, game_version: GameVersion, biomes: Mapping[str, Collection[str]]
    ):
        super().__init__(game_version)
        self._biomes = {
            namespace: tuple(base_names) for namespace, base_names in biomes.items()
        }

    def __getstate__(self) -> dict:
        state = super().__getstate__()
        state["_biomes"] = self._biomes
        return state

    def __setstate__(self, state: dict) -> None:
        super().__setstate__(state)
        self._biomes = state["_biomes"]

    def namespaces(self) -> Collection[str]:
        """An iterable of all the valid biome namespaces."""
        return self._biomes.keys()

    def base_names(self, namespace: str) -> Collection[str]:
        """An iterable of all valid base names for the given namespace."""
        return self._biomes[namespace]

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
        target_game_version = get_game_version(target_platform, target_version)
        universal_biome = self.to_universal(biome)
        return target_game_version.biome.from_universal(
            target_platform, target_version, universal_biome
        )

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
        raise NotImplementedError

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
        raise NotImplementedError


class DatabaseBiomeData(BiomeData):
    _to_universal: Mapping[tuple[str, str], Biome]
    _from_universal: Mapping[Biome, tuple[str, str]]

    def __init__(
        self,
        game_version: GameVersion,
        biomes: Mapping[str, Collection[str]],
        to_universal: Mapping[tuple[str, str], Biome],
        from_universal: Mapping[Biome, tuple[str, str]],
    ):
        super().__init__(game_version, biomes)
        self._to_universal = to_universal
        self._from_universal = from_universal

    def __getstate__(self) -> dict:
        state = super().__getstate__()
        state["_to_universal"] = self._to_universal
        state["_from_universal"] = self._from_universal
        return state

    def __setstate__(self, state: dict) -> None:
        super().__setstate__(state)
        self._to_universal = state["_to_universal"]
        self._from_universal = state["_from_universal"]

    def to_universal(self, biome: Biome) -> Biome:
        if not self._game_version.supports_version(biome.platform, biome.version):
            raise ValueError("The biome is not compatible with this version")

        try:
            return self._to_universal[(biome.namespace, biome.base_name)]
        except KeyError:
            raise BiomeTranslationError(
                f"Biome {biome} does not exist in version {self._game_version.platform} {self._game_version.min_version}"
            )

    def from_universal(
        self, target_platform: str, target_version: VersionNumber, biome: Biome
    ) -> Biome:
        if not self._game_version.supports_version(target_platform, target_version):
            raise ValueError("The target version is not compatible with this version")

        if biome.platform != "universal":
            raise ValueError("The source biome is not in the universal format")

        try:
            namespace, base_name = self._from_universal[biome]
        except KeyError:
            raise BiomeTranslationError(
                f"Biome {biome} does not exist in version {self._game_version.platform} {self._game_version.min_version}"
            )
        else:
            return Biome(target_platform, target_version, namespace, base_name)


class BiomeDataNumericalComponent(ABC):
    @abstractmethod
    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]:
        """Convert the numerical id to its namespace id"""
        raise NotImplementedError

    @abstractmethod
    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int:
        raise NotImplementedError


def load_json_biome_data(
    version_path: str,
) -> tuple[
    dict[tuple[str, str], int | None],
    dict[tuple[str, str], tuple[str, str]],
    dict[tuple[str, str], tuple[str, str]],
]:
    with open(os.path.join(version_path, "__biome_data__.json")) as f:
        data = json.load(f)

    biomes = dict[tuple[str, str], int | None]()
    to_universal = dict[tuple[str, str], tuple[str, str]]()
    from_universal = dict[tuple[str, str], tuple[str, str]]()

    for biome_str, biome_int in data["int_map"].items():
        assert isinstance(biome_str, str)
        assert isinstance(biome_int, int) or biome_int is None
        namespace, base_name = biome_str.split(":", 1)
        biomes[(namespace, base_name)] = biome_int

    for biome_str, universal_biome_str in data["version2universal"].items():
        assert isinstance(biome_str, str)
        assert isinstance(universal_biome_str, str)
        namespace, base_name = biome_str.split(":", 1)
        universal_namespace, universal_base_name = biome_str.split(":", 1)
        to_universal[(namespace, base_name)] = (
            universal_namespace,
            universal_base_name,
        )

    for universal_biome_str, biome_str in data["universal2version"].items():
        assert isinstance(biome_str, str)
        assert isinstance(universal_biome_str, str)
        namespace, base_name = biome_str.split(":", 1)
        universal_namespace, universal_base_name = biome_str.split(":", 1)
        from_universal[(universal_namespace, universal_base_name)] = (
            namespace,
            base_name,
        )

    return biomes, to_universal, from_universal

from __future__ import annotations

from functools import cache
from typing import overload, Literal, TYPE_CHECKING
from collections.abc import Sequence

from amulet.version import VersionNumber
from ._version import Version

if TYPE_CHECKING:
    from ._java_version import JavaVersion
    from ._bedrock_version import BedrockVersion


class TranslationManager:
    def __init__(self) -> None:
        self._versions: dict[str, list[Version]] = {}

    def platforms(self) -> list[str]:
        """
        Get a list of all the platforms there are Version classes for.
        These are currently 'java' and 'bedrock'
        """
        return list(self._versions.keys())

    @overload
    def versions(self, platform: Literal["java"]) -> Sequence[JavaVersion]:
        ...

    @overload
    def versions(self, platform: Literal["bedrock"]) -> Sequence[BedrockVersion]:
        ...

    def versions(self, platform: str) -> Sequence[Version]:
        """
        Get all known version classes for the platform.

        :param platform: The platform name (use :attr:`platforms` to get the valid platforms)
        :return: The version classes for the platform
        :raise: Raises a KeyError if the platform is not present.
        """
        if platform not in self._versions:
            raise KeyError(f'The requested platform "{platform}" is not present')
        return tuple(self._versions[platform])

    @overload
    def get_version(
        self, platform: Literal["java"], version_number: VersionNumber
    ) -> JavaVersion:
        ...

    @overload
    def get_version(
        self, platform: Literal["bedrock"], version_number: VersionNumber
    ) -> BedrockVersion:
        ...

    @cache  # type: ignore
    def get_version(self, platform: str, version_number: VersionNumber) -> Version:
        """
        Get a Version class for the requested platform and version number

        :param platform: The platform name (use ``TranslationManager.platforms`` to get the valid platforms)
        :param version_number: The version number or DataVersion (use ``TranslationManager.version_numbers`` to get version numbers for a given platforms)
        :return: The Version class for the given inputs.
        :raise: Raises a KeyError if it does not exist.
        """
        if platform not in self._versions:
            raise KeyError(f'The requested platform "{platform}" is not present')
        for version in self._versions[platform]:
            if version.supports_version(platform, version_number):
                return version
        raise KeyError(f"Version {platform}, {version_number} is not supported")

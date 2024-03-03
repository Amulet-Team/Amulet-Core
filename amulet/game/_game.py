from __future__ import annotations

import traceback
from functools import cache
from typing import overload, Literal, TYPE_CHECKING
from collections.abc import Sequence
from threading import RLock
import pickle
import os
import glob
import json
import gzip

from amulet.version import VersionNumber


if TYPE_CHECKING:
    from .abc import GameVersion
    from ._universal import UniversalVersion
    from .java import JavaGameVersion
    from .bedrock import BedrockGameVersion


_versions: dict[str, list[GameVersion]] | None = None
_lock = RLock()


def _compile_raw_versions() -> None:
    global _versions
    with _lock:
        json_path = os.environ.get("AMULET_GAME_VERSION_JSON_PATH")
        if json_path is None:
            raise RuntimeError("Could not find game version data.")
        from .java import JavaGameVersion
        from .bedrock import BedrockGameVersion
        from ._universal import UniversalVersion

        _versions = {}
        _versions.setdefault("universal", []).append(
            UniversalVersion.from_json(os.path.join(json_path, "versions", "universal"))
        )
        for init_path in glob.glob(
            os.path.join(glob.escape(json_path), "versions", "*", "__init__.json")
        ):
            version_path = os.path.dirname(init_path)

            with open(os.path.join(version_path, "__init__.json")) as f:
                init = json.load(f)

            platform = init["platform"]
            if platform == "bedrock":
                _versions.setdefault("bedrock", []).append(
                    BedrockGameVersion.from_json(version_path)
                )
            elif platform == "java":
                _versions.setdefault("java", []).append(
                    JavaGameVersion.from_json(version_path)
                )
            elif platform == "universal":
                pass
            else:
                raise RuntimeError
        with open(
            os.path.join(os.path.dirname(__file__), "versions.pkl.gz"), "wb"
        ) as pkl:
            pkl.write(gzip.compress(pickle.dumps(_versions)))


def _get_versions() -> dict[str, list[GameVersion]]:
    global _versions
    with _lock:
        if _versions is None:
            pkl_path = os.path.join(os.path.dirname(__file__), "versions.pkl.gz")
            if os.path.isfile(pkl_path):
                try:
                    with open(pkl_path, "rb") as pkl:
                        _versions = pickle.loads(gzip.decompress(pkl.read()))
                except:
                    traceback.print_exc()

            if _versions is None:
                _compile_raw_versions()

    assert _versions is not None
    return _versions


def game_platforms() -> list[str]:
    """
    Get a list of all the platforms there are Version classes for.
    These are currently 'java' and 'bedrock'
    """
    return list(_get_versions().keys())


@overload
def game_versions(platform: Literal["java"]) -> Sequence[JavaGameVersion]: ...


@overload
def game_versions(platform: Literal["bedrock"]) -> Sequence[BedrockGameVersion]: ...


@overload
def game_versions(platform: str) -> Sequence[GameVersion]: ...


def game_versions(platform: str) -> Sequence[GameVersion]:
    """
    Get all known version classes for the platform.

    :param platform: The platform name (use :attr:`platforms` to get the valid platforms)
    :return: The version classes for the platform
    :raises KeyError: If the platform is not present.
    """
    if platform not in _get_versions():
        raise KeyError(f'The requested platform "{platform}" is not present')
    return tuple(_get_versions()[platform])


@overload
def get_game_version(
    platform: Literal["java"], version_number: VersionNumber
) -> JavaGameVersion: ...


@overload
def get_game_version(
    platform: Literal["bedrock"], version_number: VersionNumber
) -> BedrockGameVersion: ...


@overload
def get_game_version(platform: str, version_number: VersionNumber) -> GameVersion: ...


@cache  # type: ignore
def get_game_version(platform: str, version_number: VersionNumber) -> GameVersion:
    """
    Get a Version class for the requested platform and version number

    :param platform: The platform name (use ``TranslationManager.platforms`` to get the valid platforms)
    :param version_number: The version number or DataVersion (use ``TranslationManager.version_numbers`` to get version numbers for a given platforms)
    :return: The Version class for the given inputs.
    :raises KeyError: If it does not exist.
    """
    if platform not in _get_versions():
        raise KeyError(f'The requested platform "{platform}" is not present')
    for version in _get_versions()[platform]:
        if version.supports_version(platform, version_number):
            return version
    raise KeyError(f"Version {platform}, {version_number} is not supported")

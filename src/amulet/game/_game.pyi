from collections.abc import Sequence
from typing import Literal, overload

from amulet.version import VersionNumber as VersionNumber

from ._universal import UniversalVersion as UniversalVersion
from .abc import GameVersion as GameVersion
from .bedrock import BedrockGameVersion as BedrockGameVersion
from .java import JavaGameVersion as JavaGameVersion

def game_platforms() -> list[str]:
    """
    Get a list of all the platforms there are Version classes for.
    These are currently 'java' and 'bedrock'
    """

@overload
def game_versions(platform: Literal["java"]) -> Sequence[JavaGameVersion]: ...
@overload
def game_versions(platform: Literal["bedrock"]) -> Sequence[BedrockGameVersion]: ...
@overload
def game_versions(platform: str) -> Sequence[GameVersion]: ...
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

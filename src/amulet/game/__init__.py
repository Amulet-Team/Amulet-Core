"""
A module to store data about the game including state enumerations and translations between different game versions.
"""

from ._game import game_platforms, game_versions, get_game_version
from .java import JavaGameVersion
from .bedrock import BedrockGameVersion

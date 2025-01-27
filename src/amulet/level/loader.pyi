from __future__ import annotations

import types
import typing

import amulet.level.abc.level

__all__ = [
    "LevelLoaderPathToken",
    "LevelLoaderToken",
    "NoValidLevelLoader",
    "get_level",
]

class LevelLoaderPathToken(LevelLoaderToken):
    def __init__(self, arg0: str) -> None: ...

class LevelLoaderToken:
    @typing.overload
    def __eq__(self, arg0: LevelLoaderToken) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __hash__(self) -> int: ...
    def repr(self) -> str: ...

class NoValidLevelLoader(Exception):
    pass

def get_level(token: LevelLoaderToken) -> amulet.level.abc.level.Level: ...

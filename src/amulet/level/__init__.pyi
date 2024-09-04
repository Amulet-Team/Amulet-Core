from __future__ import annotations
from amulet.level._load import NoValidLevel
from amulet.level._load import get_level
from amulet.level._load import register_level_class
from amulet.level._load import unregister_level_class
from amulet.level.abc._level._level import Level
from amulet.level.java._level import JavaLevel
import typing
from . import java

__all__ = [
    "JavaLevel",
    "Level",
    "NoValidLevel",
    "get_level",
    "java",
    "register_level_class",
    "unregister_level_class",
]

def __dir__() -> typing.Any: ...
def __getattr__(arg0: typing.Any) -> typing.Any: ...

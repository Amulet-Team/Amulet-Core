from __future__ import annotations

import typing

from amulet.level._load import (
    NoValidLevel,
    get_level,
    register_level_class,
    unregister_level_class,
)
from amulet.level.abc._level._level import Level
from amulet.level.java._level import JavaLevel

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

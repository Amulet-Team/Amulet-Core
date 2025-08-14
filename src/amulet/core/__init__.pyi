from __future__ import annotations

from . import (
    _amulet_core,
    _version,
    biome,
    block,
    block_entity,
    chunk,
    entity,
    palette,
    selection,
    version,
)

__all__: list[str] = [
    "biome",
    "block",
    "block_entity",
    "chunk",
    "compiler_config",
    "entity",
    "palette",
    "selection",
    "version",
]

def _init() -> None: ...

__version__: str
compiler_config: dict

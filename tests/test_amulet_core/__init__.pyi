from __future__ import annotations

import faulthandler as _faulthandler

from . import (
    _test_amulet_core,
    test_biome_,
    test_block_,
    test_block_entity_,
    test_chunk_,
    test_chunk_components,
    test_entity_,
    test_palette,
    test_selection_,
    test_version_,
)

__all__ = [
    "compiler_config",
    "test_biome_",
    "test_block_",
    "test_block_entity_",
    "test_chunk_",
    "test_chunk_components",
    "test_entity_",
    "test_palette",
    "test_selection_",
    "test_version_",
]

def _init() -> None: ...

compiler_config: dict

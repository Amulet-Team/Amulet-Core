from __future__ import annotations

from .leveldb_38 import (
    LevelDB38Interface as ParentInterface,
)


class LevelDB39Interface(ParentInterface):
    chunk_version = 39


export = LevelDB39Interface

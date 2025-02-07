from __future__ import annotations

import amulet.version

__all__ = ["JavaCreateArgsV1", "JavaRawLevel"]

class JavaCreateArgsV1:
    def __init__(
        self,
        overwrite: bool,
        path: str,
        version: amulet.version.VersionNumber,
        level_name: str,
    ) -> None: ...
    @property
    def level_name(self) -> str: ...
    @property
    def overwrite(self) -> bool: ...
    @property
    def path(self) -> str: ...
    @property
    def version(self) -> amulet.version.VersionNumber: ...

class JavaRawLevel:
    pass

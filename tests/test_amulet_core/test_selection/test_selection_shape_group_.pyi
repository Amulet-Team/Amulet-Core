from __future__ import annotations

import collections.abc

import amulet.core.selection.cuboid

__all__: list[str] = ["get_cuboid_ref", "get_tests"]

def get_cuboid_ref(
    arg0: amulet.core.selection.cuboid.SelectionCuboid,
) -> amulet.core.selection.cuboid.SelectionCuboid: ...
def get_tests() -> list[collections.abc.Callable[[], None]]: ...

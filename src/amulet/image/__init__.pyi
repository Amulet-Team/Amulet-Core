from __future__ import annotations

import PIL.Image

__all__ = [
    "get_missing_no_icon",
    "get_missing_pack_icon",
    "get_missing_world_icon",
    "missing_no_icon_path",
    "missing_pack_icon_path",
    "missing_world_icon_path",
]

def get_missing_no_icon() -> PIL.Image.Image: ...
def get_missing_pack_icon() -> PIL.Image.Image: ...
def get_missing_world_icon() -> PIL.Image.Image: ...

missing_no_icon_path: str
missing_pack_icon_path: str
missing_world_icon_path: str

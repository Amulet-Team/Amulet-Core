from __future__ import annotations

import glob
import importlib
import json
import os
import sys

from types import ModuleType
from typing import Dict, KeysView

from api import paths

SUPPORTED_FORMAT_VERSION = 0
SUPPORTED_META_VERSION = 0

_loaded_formats: Dict[str, ModuleType] = {}
_has_loaded_formats = False

def _find_formats(search_directory=paths.FORMATS_DIR):
    global _has_loaded_formats
    
    directories = glob.iglob(os.path.join(search_directory, "*", ""))
    py_path = os.path.join(search_directory)
    sys.path.insert(0, py_path)
    for d in directories:
        meta_path = os.path.join(d, "format.meta")
        if not os.path.exists(meta_path):
            continue

        fp = open(meta_path)
        format_info = json.load(fp)
        fp.close()

        if format_info["meta_version"] != SUPPORTED_META_VERSION:
            print(
                f'[Error] Couldn\'t enable format located in "{d}" due to unsupported meta version'
            )
            continue

        if format_info["format"]["format_version"] != SUPPORTED_FORMAT_VERSION:
            print(
                f"[Error] Couldn't enable format \"{format_info['format']['id']}\" due to unsupported format version"
            )
            continue

        modu = importlib.import_module(
            format_info["format"]["entry_point"],
            package=f"formats.{format_info['format']['id']}",
        )

        _loaded_formats[format_info["format"]["id"]] = modu

        if __debug__:
            print(
                f"[Debug] Enabled format \"{format_info['format']['id']}\", version {format_info['format']['wrapper_version']}"
            )

    if py_path in sys.path:  # Sanity check and then remove the added path
        sys.path.remove(py_path)
        
    _has_loaded_formats = True


def reload():
    _loaded_formats.clear()
    _find_formats()


def get_all_formats() -> KeysView:
    if not _has_loaded_formats:
        _find_formats()
    return _loaded_formats.keys()


def get_format(format_id: str) -> ModuleType:
    if not _has_loaded_formats:
        _find_formats()
    return _loaded_formats[format_id]


if __name__ == "__main__":
    import time

    _find_formats()
    print(_loaded_formats)
    time.sleep(5)
    reload()
    print(_loaded_formats)

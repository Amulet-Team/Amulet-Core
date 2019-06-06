from __future__ import annotations

import glob
import importlib
import json
import os
import sys

from api.paths import FORMATS_DIR

SUPPORTED_FORMAT = 0

_loaded_formats = {}

def _find_formats(search_directory=FORMATS_DIR):
    directories = glob.iglob(os.path.join(search_directory, '*', ""))
    py_path = os.path.join(search_directory)
    sys.path.insert(0, py_path)
    for d in directories:
        meta_path = os.path.join(d, "format.meta")
        if not os.path.exists(meta_path):
            continue

        fp = open(meta_path)
        format_info = json.load(fp)
        fp.close()

        if __debug__:
            print(f"[Debug] Enabled \"{format_info['format']['id']}\", version {format_info['format']['wrapper_version']}")

        modu = importlib.import_module(format_info["format"]["entry_point"], package=f"formats.{format_info['format']['id']}")
        
        _loaded_formats[format_info["format"]["id"]] = modu

    if py_path in sys.path: # Sanity check and then remove the added path
        sys.path.remove(py_path)

def reload():
    global  _loaded_formats
    _loaded_formats = {}
    _find_formats()


if __name__ == "__main__":
    import time
    _find_formats()
    time.sleep(5)
    reload()
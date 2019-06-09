from __future__ import annotations

import sys
import os
import glob
import json
import importlib

from collections import namedtuple

from typing import Dict, KeysView

from api import paths

SUPPORTED_VERSION_VERSION = 0
SUPPORTED_META_VERSION = 0

_VersionEntry = namedtuple("_VersionEntry", ("module", "format"))

_loaded_versions: Dict[str, _VersionEntry] = {}
_has_loaded_versions = False


def _find_versions(search_directory=paths.DEFINITIONS_DIR):
    global _has_loaded_versions

    directories = glob.iglob(os.path.join(search_directory, "*", ""))
    py_path = os.path.join(search_directory)
    sys.path.insert(0, py_path)
    for d in directories:
        meta_path = os.path.join(d, "version.meta")
        if not os.path.exists(meta_path):
            continue

        fp = open(meta_path)
        version_info = json.load(fp)
        fp.close()

        if version_info["meta_version"] != SUPPORTED_META_VERSION:
            print(
                f'[Error] Couldn\'t enable version located in "{d}" due to unsupported meta version'
            )
            continue

        if version_info["version"]["version"] != SUPPORTED_VERSION_VERSION:
            print(
                f"[Error] Couldn't enable version \"{version_info['version']['id']}\" due to unsupported version"
            )
            continue

        modu = importlib.import_module(
            version_info["version"]["entry_point"],
            package=f"version_definitions.{version_info['version']['id']}",
        )

        _loaded_versions[version_info["version"]["id"]] = _VersionEntry(
            modu, version_info["version"]["format"]
        )

        if __debug__:
            print(
                f"[Debug] Enabled version \"{version_info['version']['id']}\", version {version_info['version']['version']}"
            )

    if py_path in sys.path:
        sys.path.remove(py_path)

    _has_loaded_versions = True


def reload():
    global _has_loaded_versions
    _has_loaded_versions = False

    _loaded_versions.clear()
    _find_versions()


def get_all_versions() -> KeysView:
    if not _has_loaded_versions:
        _find_versions()
    return _loaded_versions.keys()


def get_version(version_id: str) -> _VersionEntry:
    if not _has_loaded_versions:
        _find_versions()
    return _loaded_versions[version_id]


if __name__ == "__main__":
    _find_versions()

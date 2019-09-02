from __future__ import annotations

import sys
import os
import glob
import json
from importlib.util import spec_from_file_location, module_from_spec

from collections import namedtuple

from typing import Dict, AbstractSet

from . import paths

SUPPORTED_VERSION_VERSION = 0
SUPPORTED_META_VERSION = 0

VersionEntry = namedtuple("VersionEntry", ("module", "format"))

_loaded_versions: Dict[str, VersionEntry] = {}
_has_loaded_versions = False


def _find_versions(search_directory: str = None):
    global _has_loaded_versions

    if not search_directory:
        search_directory = paths.DEFINITIONS_DIR

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

        spec = spec_from_file_location(
            version_info["version"]["entry_point"],
            os.path.join(
                search_directory,
                os.path.basename(os.path.dirname(d)),
                version_info["version"]["entry_point"] + ".py",
            ),
        )

        modu = module_from_spec(spec)
        spec.loader.exec_module(modu)

        _loaded_versions[version_info["version"]["id"]] = VersionEntry(
            modu, version_info["version"]["format"]
        )

        if __debug__:
            print(
                f"[Debug] Enabled version \"{version_info['version']['id']}\", version {version_info['version']['version']}"
            )

    if py_path in sys.path:
        sys.path.remove(py_path)

    _has_loaded_versions = True


def reload(search_directory: str = None):
    """
    Reloads all versions in the given directory

    :param search_directory: The directory to search for, defaults to :py:data:`api.paths.DEFINITIONS_DIR`
    """
    global _has_loaded_versions
    _has_loaded_versions = False

    _loaded_versions.clear()
    _find_versions(search_directory)


def get_all_versions() -> AbstractSet[str]:
    """
    :return: The names of all loaded versions
    """
    if not _has_loaded_versions:
        _find_versions()
    return _loaded_versions.keys()


def get_version(version_id: str) -> VersionEntry:
    """
    Gets the module for the version with the given ``version_id``

    :param version_id: The id for the desired loaded version
    :return: The ``VersionEntry`` for the specified ``version_id``
    """
    if not _has_loaded_versions:
        _find_versions()
    return _loaded_versions[version_id]


if __name__ == "__main__":
    _find_versions()

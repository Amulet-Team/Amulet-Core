from __future__ import annotations

import glob
import importlib
import json
import os

from typing import Tuple, AbstractSet, Dict

from .interfaces.interface import Interface
from ..api import paths
from ..api.errors import InterfaceLoaderNoneMatched

_loaded_interfaces: Dict[str, Interface] = {}
_has_loaded_interfaces = False

SUPPORTED_INTERFACE_VERSION = 0
SUPPORTED_META_VERSION = 0


def _find_interfaces(search_directory: str = None):
    global _has_loaded_interfaces

    if not search_directory:
        search_directory = paths.INTERFACES_DIR

    directories = glob.iglob(os.path.join(search_directory, "*", ""))
    for d in directories:
        meta_path = os.path.join(d, "interface.meta")
        if not os.path.exists(meta_path):
            continue

        with open(meta_path) as fp:
            interface_info = json.load(fp)

        if interface_info["meta_version"] != SUPPORTED_META_VERSION:
            print(
                f'[Error] Couldn\'t enable interface located in "{d}" due to unsupported meta version'
            )
            continue

        if interface_info["interface"]["interface_version"] != SUPPORTED_INTERFACE_VERSION:
            print(
                f"[Error] Couldn't enable interface \"{interface_info['interface']['id']}\" due to unsupported interface version"
            )
            continue

        spec = importlib.util.spec_from_file_location(
            interface_info["interface"]["entry_point"],
            os.path.join(d, interface_info["interface"]["entry_point"] + ".py"),
        )
        modu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modu)

        if not hasattr(modu, "INTERFACE_CLASS"):
            print(
                f"[Error] Interface \"{interface_info['interface']['id']}\" is missing the INTERFACE_CLASS attribute"
            )
            continue

        _loaded_interfaces[interface_info["interface"]["id"]] = modu.INTERFACE_CLASS()

        if __debug__:
            print(
                f"[Debug] Enabled interface \"{interface_info['interface']['id']}\", version {interface_info['interface']['wrapper_version']}"
            )

    _has_loaded_interfaces = True


def reload(search_directory: str = None):
    """
    Reloads all interfaces in the given directory

    :param search_directory: The directory to search for, defaults to :py:data:`api.paths.FORMATS_DIR`
    """
    _loaded_interfaces.clear()
    _find_interfaces(search_directory)


def get_all_loaded_interfaces() -> AbstractSet[str]:
    """
    :return: The identifiers of all loaded interfaces
    """
    if not _has_loaded_interfaces:
        _find_interfaces()
    return _loaded_interfaces.keys()


def get_interface(interface_id: str) -> Interface:
    """
    Gets the class for the interface with the given ``interface_id``

    :param interface_id: The interface id for the desired loaded interface
    :return: The class for the interface
    """
    if not _has_loaded_interfaces:
        _find_interfaces()
    return _loaded_interfaces[interface_id]


def identify(identifier: Tuple) -> str:
    if not _has_loaded_interfaces:
        _find_interfaces()

    for interface_name, interface_instance in _loaded_interfaces.items():
        if interface_instance.identify(identifier):
            return interface_name

    raise InterfaceLoaderNoneMatched("Could not find a matching interface")


if __name__ == "__main__":
    import time

    _find_interfaces()
    print(_loaded_interfaces)
    time.sleep(1)
    reload()
    print(_loaded_interfaces)

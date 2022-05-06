from typing import Optional, Dict
import pkgutil
import importlib
import inspect
import logging

from amulet.api.errors import LoaderNoneMatched
from .base_leveldb_interface import BaseLevelDBInterface

_interfaces: Optional[Dict[int, BaseLevelDBInterface]] = None

log = logging.getLogger(__name__)


def get_interface(interface_version: int):
    global _interfaces
    if _interfaces is None:
        _interfaces = {}

        for _, module_name, _ in pkgutil.walk_packages(__path__, __name__ + "."):
            modu = importlib.import_module(module_name)
            c = getattr(modu, "export", None)
            if inspect.isclass(c) and issubclass(c, BaseLevelDBInterface):
                if c.chunk_version in _interfaces:
                    log.error(
                        f"Multiple Bedrock chunk interfaces with chunk_version={c.chunk_version}"
                    )
                else:
                    _interfaces[c.chunk_version] = c()

    if interface_version not in _interfaces:
        raise LoaderNoneMatched(
            f"Could not find a leveldb interface for chunk version {interface_version}"
        )

    return _interfaces[interface_version]

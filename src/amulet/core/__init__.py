import logging as _logging

from . import _version

__version__ = _version.get_versions()["version"]

# init a default logger
_logging.basicConfig(level=_logging.INFO, format="%(levelname)s - %(message)s")


def _init() -> None:
    import os
    import sys
    import ctypes

    if sys.platform == "win32":
        lib_path = os.path.join(os.path.dirname(__file__), "amulet_core.dll")
    elif sys.platform == "darwin":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_core.dylib")
    elif sys.platform == "linux":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_core.so")
    else:
        raise RuntimeError(f"Unsupported platform {sys.platform}")

    # Import dependencies
    import amulet.zlib
    import amulet.nbt

    # Load the shared library
    ctypes.cdll.LoadLibrary(lib_path)

    from ._amulet_core import init

    init(sys.modules[__name__])


_init()

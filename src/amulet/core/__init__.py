import logging as _logging

from . import _version

__version__ = _version.get_versions()["version"]

# init a default logger
_logging.basicConfig(level=_logging.INFO, format="%(levelname)s - %(message)s")


def _init() -> None:
    import os
    import sys

    if os.environ.get("AMULET_SKIP_COMPILE", None):
        return

    # Import dependencies
    import amulet.utils
    import amulet.zlib
    import amulet.nbt

    from ._amulet_core import init

    init(sys.modules[__name__])


_init()
del _init

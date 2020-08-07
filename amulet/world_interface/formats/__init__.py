from __future__ import annotations

import os
from amulet.world_interface.loader import Loader

SUPPORTED_FORMAT_VERSION = 0
SUPPORTED_META_VERSION = 0

FORMATS_DIRECTORY = os.path.dirname(__file__)

loader = Loader(
    "format",
    FORMATS_DIRECTORY,
    SUPPORTED_META_VERSION,
    SUPPORTED_FORMAT_VERSION,
    create_instance=False,
)

if __name__ == "__main__":
    import time

    print(loader.get_all())
    time.sleep(1)
    loader.reload()
    print(loader.get_all())

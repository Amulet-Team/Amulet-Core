from __future__ import annotations

import os
from amulet.world_interface.loader import Loader

SUPPORTED_TRANSLATOR_VERSION = 0
SUPPORTED_META_VERSION = 0

TRANSLATORS_DIRECTORY = os.path.dirname(__file__)

loader = Loader(
    "translator",
    TRANSLATORS_DIRECTORY,
    SUPPORTED_META_VERSION,
    SUPPORTED_TRANSLATOR_VERSION,
)

if __name__ == "__main__":
    import time

    print(loader.get_all())
    time.sleep(1)
    loader.reload()
    print(loader.get_all())

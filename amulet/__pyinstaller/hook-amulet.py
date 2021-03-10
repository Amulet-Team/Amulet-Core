import pkgutil
import sys
import os

import amulet
from amulet import level
from amulet import operations

AMULET_PATH = amulet.__path__[0]

hiddenimports = (
    [name for _, name, _ in pkgutil.walk_packages(level.__path__, level.__name__ + ".")]
    + [
        name
        for _, name, _ in pkgutil.walk_packages(
            operations.__path__, operations.__name__ + "."
        )
    ]
    + ["amulet.api.structure"]
)

if sys.platform == "linux":
    binaries = [
        (
            os.path.join(AMULET_PATH, "libs", "leveldb", "libleveldb.so"),
            os.path.join(".", "amulet", "libs", "leveldb"),
        ),
    ]
elif sys.platform == "win32":
    if sys.maxsize > 2 ** 32:  # 64 bit python
        binaries = [
            (
                os.path.join(AMULET_PATH, "libs", "leveldb", "LevelDB-MCPE-64.dll"),
                os.path.join(".", "amulet", "libs", "leveldb"),
            ),
        ]
    else:
        binaries = [
            (
                os.path.join(AMULET_PATH, "libs", "leveldb", "LevelDB-MCPE-32.dll"),
                os.path.join(".", "amulet", "libs", "leveldb"),
            )
        ]

elif sys.platform == "darwin":
    binaries = [
        (
            os.path.join(AMULET_PATH, "libs", "leveldb", "libleveldb.dylib"),
            os.path.join(".", "amulet", "libs", "leveldb"),
        ),
    ]
else:
    raise Exception(f"Unsupported platform {sys.platform}")

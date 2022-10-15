import pkgutil
from PyInstaller.utils.hooks import collect_data_files

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

datas = collect_data_files("amulet")

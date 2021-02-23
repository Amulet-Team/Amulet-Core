from PyInstaller.utils.hooks import collect_data_files
import pkgutil
from amulet import level

hiddenimports = [
    name for _, name, _ in pkgutil.walk_packages(level.__path__, level.__name__ + ".")
]

datas = collect_data_files("amulet", excludes=["__pyinstaller"])

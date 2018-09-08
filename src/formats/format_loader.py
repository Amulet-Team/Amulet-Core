import os
import sys
import traceback
import importlib
import importlib.util
import glob
import time
from types import ModuleType
from typing import Tuple, Optional

from api.paths import FORMATS_DIR
from api.world import World

SUPPORTED_FORMAT = 0

class _FormatLoader:

    REQUIRED_ATTRIBUTES = [
        "LEVEL_CLASS",
        "REGION_CLASS",
        "CHUNK_CLASS",
        "MATERIALS_CLASS",
        "identify",
    ]

    _loaded_formats = {}

    def __init__(self, search_directory=FORMATS_DIR):
        self.search_directory = search_directory

        self._find_formats()

    def _find_formats(self):
        directories = glob.glob(os.path.join(self.search_directory, "*", ""))
        sys.path.insert(0, os.path.join(self.search_directory))
        for d in directories:
            if not os.path.exists(os.path.join(d, "__init__.py")):
                continue

            format_name = os.path.basename(os.path.dirname(d)[2:])
            success, module = self.load_format(format_name)
            if success:
                self._loaded_formats[format_name] = module
                if __debug__:
                    print(
                        f"[Debug] Enabled \"{format_name}\" format, version {getattr(module, '__version__', -1)}"
                    )

    @staticmethod
    def load_format(directory: str) -> Tuple[bool, object]:
        try:
            format_module = importlib.import_module(os.path.basename(directory))
        except ImportError:
            traceback.print_exc()
            time.sleep(0.01)
            print(
                'Could not import the "{}" format due to the above Exception'.format(
                    directory
                )
            )
            return False, None

        if not (
            hasattr(format_module, "LEVEL_CLASS") and hasattr(format_module, "identify")
        ):
            print(
                'Disabled the "{}" format due to missing required attributes'.format(
                    directory
                )
            )
            return False, None

        if getattr(format_module, "__format__", -1) != SUPPORTED_FORMAT:
            raise ImportError(f"\"{format_module.__name__}\" world loader format mismatches the supported format")

        return True, format_module

    def get_loaded_formats(self) -> dict:
        return dict(self._loaded_formats)

    def reload(self):
        self._find_formats()

    def add_external_format(self, name: str, module: ModuleType) -> bool:
        if (
            isinstance(name, str)
            and isinstance(module, ModuleType)
            and name not in self._loaded_formats
        ):
            self._loaded_formats[name] = module
            return True

        elif name in self._loaded_formats:
            return False

        else:
            raise Exception(
                "To add an external format you must supply a name and a module object!"
            )

    def identify_world_format_str(self, directory: str) -> str:
        for name, module in self._loaded_formats.items():
            if module.identify(directory):
                return name

        raise ModuleNotFoundError("Could not find a valid format loader")

    def load_world(self, directory: str) -> World:
        for name, module in self._loaded_formats.items():
            if module.identify(directory):
                return module.LEVEL_CLASS.load(directory)

        raise ModuleNotFoundError("Could not find a valid format loader")


loader = _FormatLoader()


def load_world(world_directory: str) -> Optional[World]:
    try:
        return loader.load_world(world_directory)
    except ModuleNotFoundError:
        return None

from __future__ import annotations

import os
import glob
import sys
import traceback
from importlib import import_module
from typing import Tuple, List

from api.paths import DEFINITIONS_DIR
from api.world import World


class _WorldLoader:
    """
    Class responsible for loading worlds
    """

    def __init__(self):
        self._identifiers = {}
        for definition in glob.iglob(os.path.join(DEFINITIONS_DIR, "**", "*.py")):

            module_name = os.path.basename(os.path.dirname(definition))
            if not definition.endswith(f"{module_name}.py"):
                continue

            sys.path.insert(0, os.path.dirname(definition))
            definition_name = os.path.basename(os.path.dirname(definition))
            try:
                module = import_module(os.path.basename(definition)[:-3])
                if not (
                    hasattr(module, "load")
                    or hasattr(module, "identify")
                    or hasattr(module, "FORMAT")
                ):
                    raise ValueError()

                self._identifiers[definition_name] = module
            except:
                if __debug__:
                    traceback.print_exc()
                pass
            sys.path.remove(os.path.dirname(definition))

    def identify(self, directory: str) -> Tuple[str, str]:
        """
        Identifies the level format the world is in and the versions definitions that match
        the world. Note: Since Minecraft Java versions below 1.12 lack version identifiers, they
        will always be loaded with 1.12 definitions.

        :param directory: The directory of the world
        :return: The version definitions name for the world and the format loader that would be used
        """
        for name, module in self._identifiers.items():
            if module.identify(directory):
                return name, module.FORMAT
            elif __debug__:
                print(f"{name} rejected the world")

        raise ModuleNotFoundError("Could not find a matching format loader")

    def load_world(self, directory: str, format: str = None) -> World:
        """
        Loads the world located at the given directory with the specified version/format loader

        :param directory: The directory of the world
        :param format: The loader name to use
        :return: The loaded world
        """

        format = format or loader.identify(directory)[0]

        if not format in self._identifiers:
            raise ModuleNotFoundError(f"Could not find format loader {format}")

        module = self._identifiers[format]
        return module.load(directory)

    def get_loaded_identifiers(self) -> List[str]:
        """
        List all format loader identifiers

        :return: List of all format identifiers
        """

        return list(self._identifiers.keys())


loader = _WorldLoader()
load_world = loader.load_world
identify = loader.identify

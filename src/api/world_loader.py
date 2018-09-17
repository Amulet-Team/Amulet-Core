import os
import glob
import sys
import traceback
from importlib import import_module
from typing import Tuple

from api.paths import DEFINITIONS_DIR
from api.world import World


class _WorldLoader:

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
        for name, module in self._identifiers.items():
            if module.identify(directory):
                return name, module.FORMAT

        raise ModuleNotFoundError("Could not find a valid format loader")

    def load_world(self, directory: str) -> World:
        for module in self._identifiers.values():
            if module.identify(directory):
                return module.load(directory)

        raise ModuleNotFoundError()


loader = _WorldLoader()
load_world = loader.load_world

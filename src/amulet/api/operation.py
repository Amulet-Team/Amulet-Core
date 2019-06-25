from __future__ import annotations

from abc import abstractmethod
import glob
from importlib import import_module
from os.path import basename, join
import sys

from .paths import OPERATIONS_DIR

_imported_operations = False
OPERATIONS = {}


class Operation:
    @abstractmethod
    def run_operation(self, world):
        pass


def register(operation_name):
    """
    Registers the decorated class as an Operation with the supplied operation name

    :param operation_name: The identifying name for the Operation
    """

    def wrapper(clazz):
        if operation_name not in OPERATIONS:
            OPERATIONS[operation_name] = clazz

        return clazz

    return wrapper


def reload_operations():
    """
    Reloads all found Operations found at the directory pointed at by :py:data:`api.paths.OPERATIONS_DIR`
    """
    global OPERATIONS
    OPERATIONS = {}
    _import_operations()


def _import_operations():
    global _imported_operations
    sys.path.insert(0, OPERATIONS_DIR)
    _verify_path_len = len(sys.path)

    for f in glob.glob(join(OPERATIONS_DIR, "*.py")):
        import_module(basename(f)[:-3])

    if len(sys.path) == _verify_path_len:
        del sys.path[0]
    _imported_operations = True


if not _imported_operations:
    _import_operations()

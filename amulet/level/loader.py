from __future__ import annotations

import importlib.util
import os
from typing import AbstractSet, Any, Dict

import amulet
from amulet import log
from amulet.api.errors import LoaderNoneMatched


class Loader:
    def __init__(
        self,
        object_type: str,
        directory: str,
        create_instance=True,
    ):
        self._object_type = object_type
        self._objects: Dict[str, Any] = {}
        self._create_instance = create_instance
        self._recursive_find(directory)

    def _load_obj(self, path: str) -> bool:
        if os.path.isdir(path):
            py_path = os.path.join(path, "__init__.py")
            if not os.path.isfile(py_path):
                return False
            import_path = ".".join(
                os.path.normpath(
                    os.path.relpath(
                        path, os.path.dirname(os.path.dirname(amulet.__file__))
                    )
                ).split(os.sep)
            )
            obj_name = os.path.basename(path)
        elif os.path.isfile(path):
            if not path.endswith(".py"):
                return False
            py_path = path
            import_path = ".".join(
                os.path.normpath(
                    os.path.relpath(
                        path[:-3], os.path.dirname(os.path.dirname(amulet.__file__))
                    )
                ).split(os.sep)
            )
            obj_name = os.path.basename(path[:-3])
        else:
            return False

        with open(py_path) as f:
            first_line = f.readline()
        if first_line.strip() == f"# meta {self._object_type}":
            if obj_name in self._objects:
                log.error(
                    f"Multiple {self._object_type} classes with the name {obj_name}"
                )
                return False
            modu = importlib.import_module(import_path)

            if not hasattr(modu, "export"):
                log.error(
                    f'{self._object_type} "{obj_name}" is missing the export attribute'
                )
                return False

            c = getattr(modu, "export")
            if self._create_instance:
                self._objects[obj_name] = c()
            else:
                self._objects[obj_name] = c

            log.debug(f'Enabled {self._object_type} "{obj_name}"')
            return True
        return False

    def _recursive_find(self, path: str):
        if os.path.isdir(path):
            if not self._load_obj(path):
                for p in os.listdir(path):
                    self._recursive_find(os.path.join(path, p))
        elif os.path.isfile(path):
            self._load_obj(path)

    def keys(self) -> AbstractSet[str]:
        """
        :return: The identifiers of all loaded objects
        """
        return self._objects.keys()

    def get(self, identifier: Any) -> Any:
        """
        Given an ``identifier`` will find a valid class and return it

        :param identifier: The identifier for the desired loaded object
        :return: The class for the object
        """
        object_id = self.identify(identifier)
        return self._objects[object_id]

    def identify(self, identifier: Any) -> str:

        for object_name, obj in self._objects.items():
            if obj.is_valid(identifier):
                return object_name

        raise LoaderNoneMatched(
            f"Could not find a matching {self._object_type} for {identifier}"
        )

    def __contains__(self, item: str):
        return item in self._objects

    def report(self):
        print(f"{self._object_type} objects")
        for obj_name, obj in self._objects.items():
            print(obj_name, obj)


Formats = Loader("format", "./formats", create_instance=False)
Interfaces = Loader("interface", "./interfaces")
Translators = Loader("translator", "./translators")


if __name__ == "__main__":
    Formats.report()
    Interfaces.report()
    Translators.report()

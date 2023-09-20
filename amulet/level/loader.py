from __future__ import annotations

import importlib
from typing import AbstractSet, Any, Dict
import pkgutil
import logging
import inspect

from amulet.api.errors import LoaderNoneMatched
from amulet.api.wrapper import FormatWrapper, Interface, Translator

log = logging.getLogger(__name__)

ParentPackage = ".".join(__name__.split(".")[:-1])


class Loader:
    def __init__(
        self,
        base_class,
        object_type: str,
        package_name: str,
        create_instance=True,
    ):
        self._base_class = base_class
        self._object_type = object_type
        self._objects: Dict[str, Any] = {}
        self._create_instance = create_instance
        self._recursive_find(package_name)

    def _recursive_find(self, module_name: str):
        module = importlib.import_module(module_name)

        c = getattr(module, "export", None)
        if inspect.isclass(c) and issubclass(c, self._base_class):
            if self._create_instance:
                self._objects[module_name] = c()
            else:
                self._objects[module_name] = c

            log.debug(f'Enabled {self._object_type} "{module_name}"')

        elif hasattr(module, "__path__"):
            for _, sub_module_name, ispkg in pkgutil.iter_modules(
                module.__path__, module.__name__ + "."
            ):
                self._recursive_find(sub_module_name)

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
        if not self._objects:
            raise Exception(f"No {self._object_type} loaders found.")
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


Translators = Loader(Translator, "translator", f"{ParentPackage}.translators")
Interfaces = Loader(Interface, "interface", f"{ParentPackage}.interfaces")
Formats = Loader(
    FormatWrapper, "format", f"{ParentPackage}.formats", create_instance=False
)


if __name__ == "__main__":
    Formats.report()
    Interfaces.report()
    Translators.report()

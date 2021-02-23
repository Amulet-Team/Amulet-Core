from __future__ import annotations

import importlib
from typing import AbstractSet, Any, Dict
import pkgutil

import amulet
from amulet import log
from amulet.api.errors import LoaderNoneMatched
from amulet.api.wrapper import FormatWrapper, Interface, Translator

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
        self._recursive_find(f"{ParentPackage}.{package_name}")

    def _load_obj(self, module_name: str):
        modu = importlib.import_module(module_name)
        if hasattr(modu, "export"):
            c = getattr(modu, "export")
            if issubclass(c, self._base_class):
                if self._create_instance:
                    self._objects[module_name] = c()
                else:
                    self._objects[module_name] = c
            else:
                log.error(
                    f"export for {module_name} must be a subclass of {self._base_class}"
                )
            log.debug(f'Enabled {self._object_type} "{module_name}"')

    def _recursive_find(self, package_name: str):
        package = importlib.import_module(package_name)
        package_prefix = package.__name__ + "."

        # python file support
        for _, name, _ in pkgutil.walk_packages(package.__path__, package_prefix):
            self._load_obj(name)

        # pyinstaller support
        toc = set()
        for importer in pkgutil.iter_importers(amulet.__name__):
            if hasattr(importer, "toc"):
                toc |= importer.toc
        for module_name in toc:
            if module_name.startswith(package_prefix):
                self._load_obj(module_name)

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


Translators = Loader(Translator, "translator", "translators")
Interfaces = Loader(Interface, "interface", "interfaces")
Formats = Loader(FormatWrapper, "format", "formats", create_instance=False)


if __name__ == "__main__":
    Formats.report()
    Interfaces.report()
    Translators.report()

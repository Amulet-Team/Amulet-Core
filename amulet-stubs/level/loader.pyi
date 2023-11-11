from _typeshed import Incomplete
from amulet.api.errors import LoaderNoneMatched as LoaderNoneMatched
from amulet.api.wrapper import FormatWrapper as FormatWrapper, Interface as Interface, Translator as Translator
from typing import AbstractSet, Any, Generic, TypeVar

T = TypeVar('T')
log: Incomplete
ParentPackage: Incomplete

class Loader(Generic[T]):
    _base_class: Incomplete
    _object_type: Incomplete
    _objects: Incomplete
    _create_instance: Incomplete
    def __init__(self, base_class, object_type: str, package_name: str, create_instance: bool = ...) -> None: ...
    def _recursive_find(self, module_name: str): ...
    def keys(self) -> AbstractSet[str]:
        """
        :return: The identifiers of all loaded objects
        """
    def get(self, identifier: Any) -> T:
        """
        Given an ``identifier`` will find a valid class and return it

        :param identifier: The identifier for the desired loaded object
        :return: The class for the object
        """
    def identify(self, identifier: Any) -> str: ...
    def __contains__(self, item: str): ...
    def report(self) -> None: ...

Translators: Incomplete
Interfaces: Incomplete
Formats: Incomplete

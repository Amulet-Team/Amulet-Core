from _typeshed import Incomplete
from amulet.version import AbstractVersion as AbstractVersion, VersionContainer as VersionContainer

class Biome(VersionContainer):
    _namespace: Incomplete
    _base_name: Incomplete
    def __init__(self, version: AbstractVersion, namespace: str, base_name: str) -> None:
        '''
        Constructs a :class:`Biome` instance.

        >>> plains = Biome("minecraft", "plains")

        :param namespace: The string namespace of the biome. eg `minecraft`
        :param base_name: The string base name of the biome. eg `plains`
        :param version: The game version this biome is defined in.
            If omitted/None it will default to the highest version the container it is used in supports.
        '''
    def _data(self): ...
    def __hash__(self): ...
    def __eq__(self, other): ...
    def __gt__(self, other): ...
    def __lt__(self, other): ...
    def __repr__(self) -> str: ...
    @property
    def namespace(self) -> str:
        '''
        The namespace of the biome represented by the :class:`Biome` object.

        >>> plains = Biome("minecraft", "plains")
        >>> plains.namespace
        "minecraft"

        :return: The namespace of the biome
        '''
    @property
    def base_name(self) -> str:
        '''
        The base name of the biome represented by the :class:`Biome` object.

        >>> plains = Biome("minecraft", "plains")
        >>> plains.base_name
        "plains"

        :return: The base name of the biome
        '''

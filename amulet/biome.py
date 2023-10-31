from typing import Optional
from amulet.game_version import AbstractGameVersion


class Biome:
    def __init__(
        self,
        namespace: str,
        base_name: str,
        version: Optional[AbstractGameVersion] = None,
    ):
        """
        Constructs a :class:`Biome` instance.

        >>> plains = Biome("minecraft", "plains")

        :param namespace: The string namespace of the biome. eg `minecraft`
        :param base_name: The string base name of the biome. eg `plains`
        :param version: The game version this biome is defined in.
            If omitted/None it will default to the highest version the container it is used in supports.
        """
        self._namespace = str(namespace)
        self._base_name = str(base_name)
        if version is not None and not isinstance(version, AbstractGameVersion):
            raise TypeError("Invalid version", version)
        self._version = version

    def _data(self):
        return self._namespace, self._base_name, self._version

    def __hash__(self):
        return hash(self._data())

    def __eq__(self, other):
        if not isinstance(other, Biome):
            return NotImplemented
        return self._data() == other._data()

    def __gt__(self, other):
        if not isinstance(other, Biome):
            return NotImplemented
        return hash(self) > hash(other)

    def __lt__(self, other):
        if not isinstance(other, Biome):
            return NotImplemented
        return hash(self) < hash(other)

    def __repr__(self):
        return f"Biome({self.namespace!r}, {self.base_name!r}, {self.version!r})"

    @property
    def namespace(self) -> str:
        """
        The namespace of the biome represented by the :class:`Biome` object.

        >>> plains = Biome("minecraft", "plains")
        >>> plains.namespace
        "minecraft"

        :return: The namespace of the biome
        """
        return self._namespace

    @property
    def base_name(self) -> str:
        """
        The base name of the biome represented by the :class:`Biome` object.

        >>> plains = Biome("minecraft", "plains")
        >>> plains.base_name
        "plains"

        :return: The base name of the biome
        """
        return self._base_name

    @property
    def version(self) -> Optional[AbstractGameVersion]:
        """
        The game version this biome is defined in.
        Note that this may be None.
        """
        return self._version

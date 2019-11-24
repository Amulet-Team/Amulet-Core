import amulet_nbt


class BlockEntity:
    def __init__(
        self,
        namespace: str,
        base_name: str,
        x: int,
        y: int,
        z: int,
        nbt: amulet_nbt.NBTFile,
    ):
        self._namespace = namespace
        self._base_name = base_name
        self._namespaced_name = ("" if namespace == "" else f"{namespace}:") + base_name
        self._x = x
        self._y = y
        self._z = z
        self._nbt = nbt

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the block entity represented by the BlockEntity object (IE: `minecraft:creeper`)
        If the given namespace is an empty string it will just return the base name.

        :return: The namespace:base_name of the block entity or just base_name if no namespace
        """
        return self._namespaced_name

    @property
    def namespace(self) -> str:
        """
        The namespace of the block entity represented by the BlockEntity object (IE: `minecraft`)

        :return: The namespace of the block entity
        """
        return self._namespace

    @namespace.setter
    def namespace(self, value: str):
        self._namespace = value

    @property
    def base_name(self) -> str:
        """
        The base name of the block entity represented by the BlockEntity object (IE: `creeper`, `pig`)

        :return: The base name of the block entity
        """
        return self._base_name

    @base_name.setter
    def base_name(self, value: str):
        self._base_name = value

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value

    @property
    def z(self) -> int:
        return self._z

    @z.setter
    def z(self, value: int):
        self._z = value

    @property
    def nbt(self) -> amulet_nbt.NBTFile:
        """
        The nbt behind the BlockEntity object

        :return: An amulet_nbt.NBTFile
        """
        return self._nbt

    @nbt.setter
    def nbt(self, value: str):
        self._nbt = value

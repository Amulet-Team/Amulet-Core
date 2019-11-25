import amulet_nbt


class Entity:
    def __init__(self, namespace: str, base_name: str, x: float, y: float, z: float, nbt: amulet_nbt.NBTFile):
        self._namespace = namespace
        self._base_name = base_name
        self._namespaced_name = None
        self._gen_namespaced_name()
        self._x = x
        self._y = y
        self._z = z
        self._nbt = nbt

    def _gen_namespaced_name(self):
        self._namespaced_name = ('' if self.namespace in ['', None] else f'{self.namespace}:') + self.base_name

    def __repr__(self):
        return f'Entity[{self.namespaced_name}, {self.x}, {self.y}, {self.z}]'

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the block entity represented by the BlockEntity object (IE: `minecraft:creeper`)
        If the given namespace is an empty string it will just return the base name.

        :return: The namespace:base_name of the block entity or just base_name if no namespace
        """
        return self._namespaced_name

    @namespaced_name.setter
    def namespaced_name(self, value: str):
        self._namespaced_name = value
        if ':' in value:
            self._namespace, self._base_name = value.split(':', 1)
        else:
            self._namespace, self._base_name = None, value

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
        self._gen_namespaced_name()

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
        self._gen_namespaced_name()

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float):
        self._x = value

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float):
        self._y = value

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float):
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
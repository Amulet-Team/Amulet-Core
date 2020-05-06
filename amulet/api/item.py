import amulet_nbt


class Item(amulet_nbt.TAG_Compound):
    """
    {
        "namespace": TAG_String,
        "base_name": TAG_String,
        "metadata": TAG_Compound
    }
    """

    def __init__(self, namespace: str, base_name: str, metadata: dict = None):
        super().__init__(
            {
                "namespace": amulet_nbt.TAG_String(namespace),
                "base_name": amulet_nbt.TAG_String(base_name),
                "metadata": amulet_nbt.TAG_Compound(metadata or {}),
            }
        )

    @property
    def namespace(self) -> str:
        return self.value["namespace"].value

    @property
    def base_name(self) -> str:
        return self.value["base_name"].value

    @property
    def metadata(self) -> amulet_nbt.TAG_Compound:
        return self.value["metadata"].value


class BlockItem(amulet_nbt.TAG_Compound):
    """
    {
        "namespace": TAG_String,
        "base_name": TAG_String,
        "properties": TAG_Compound
        "metadata": TAG_Compound
    }
    """

    def __init__(
        self,
        namespace: str,
        base_name: str,
        properties: dict = None,
        metadata: dict = None,
    ):
        super().__init__(
            {
                "namespace": amulet_nbt.TAG_String(namespace),
                "base_name": amulet_nbt.TAG_String(base_name),
                "properties": amulet_nbt.TAG_Compound(properties or {}),
                "metadata": amulet_nbt.TAG_Compound(metadata or {}),
            }
        )

    @property
    def namespace(self) -> str:
        return self.value["namespace"].value

    @property
    def base_name(self) -> str:
        return self.value["base_name"].value

    @property
    def properties(self) -> amulet_nbt.TAG_Compound:
        return self.value["properties"].value

    @property
    def metadata(self) -> amulet_nbt.TAG_Compound:
        return self.value["metadata"].value

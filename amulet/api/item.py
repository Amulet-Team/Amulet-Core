from amulet_nbt import CompoundTag, StringTag


class Item(CompoundTag):
    """
    {
        "namespace": StringTag,
        "base_name": StringTag,
        "metadata": CompoundTag
    }
    """

    def __init__(self, namespace: str, base_name: str, metadata: dict = None):
        super().__init__(
            {
                "namespace": StringTag(namespace),
                "base_name": StringTag(base_name),
                "metadata": CompoundTag(metadata or {}),
            }
        )

    @property
    def namespace(self) -> str:
        return self["namespace"].py_str

    @property
    def base_name(self) -> str:
        return self["base_name"].py_str

    @property
    def metadata(self) -> CompoundTag:
        return self["metadata"]


class BlockItem(CompoundTag):
    """
    {
        "namespace": StringTag,
        "base_name": StringTag,
        "properties": CompoundTag
        "metadata": CompoundTag
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
                "namespace": StringTag(namespace),
                "base_name": StringTag(base_name),
                "properties": CompoundTag(properties or {}),
                "metadata": CompoundTag(metadata or {}),
            }
        )

    @property
    def namespace(self) -> str:
        return self["namespace"].py_str

    @property
    def base_name(self) -> str:
        return self["base_name"].py_str

    @property
    def properties(self) -> CompoundTag:
        return self["properties"]

    @property
    def metadata(self) -> CompoundTag:
        return self["metadata"]

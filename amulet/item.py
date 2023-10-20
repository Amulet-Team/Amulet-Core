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
        return self.get_string("namespace").py_str

    @property
    def base_name(self) -> str:
        return self.get_string("base_name").py_str

    @property
    def metadata(self) -> CompoundTag:
        return self.get_compound("metadata")


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
        return self.get_string("namespace").py_str

    @property
    def base_name(self) -> str:
        return self.get_string("base_name").py_str

    @property
    def properties(self) -> CompoundTag:
        return self.get_compound("properties")

    @property
    def metadata(self) -> CompoundTag:
        return self.get_compound("metadata")

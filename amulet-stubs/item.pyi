from amulet_nbt import CompoundTag

class Item(CompoundTag):
    '''
    {
        "namespace": StringTag,
        "base_name": StringTag,
        "metadata": CompoundTag
    }
    '''
    def __init__(self, namespace: str, base_name: str, metadata: dict = ...) -> None: ...
    @property
    def namespace(self) -> str: ...
    @property
    def base_name(self) -> str: ...
    @property
    def metadata(self) -> CompoundTag: ...

class BlockItem(CompoundTag):
    '''
    {
        "namespace": StringTag,
        "base_name": StringTag,
        "properties": CompoundTag
        "metadata": CompoundTag
    }
    '''
    def __init__(self, namespace: str, base_name: str, properties: dict = ..., metadata: dict = ...) -> None: ...
    @property
    def namespace(self) -> str: ...
    @property
    def base_name(self) -> str: ...
    @property
    def properties(self) -> CompoundTag: ...
    @property
    def metadata(self) -> CompoundTag: ...

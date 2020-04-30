from typing import Dict, Union, Iterable
from amulet.api.block import Block
from amulet.api.data_types import VersionIdentifierType
import amulet_nbt


class MetaBlock(Block):
    def __init__(
        self,
        namespace: str,
        base_name: str,
        properties: Dict[str, amulet_nbt.BaseValueType] = None,
        extra_blocks: Union[Block, Iterable[Block]] = None,
        version: VersionIdentifierType = None
    ):
        super().__init__(namespace, base_name, properties, extra_blocks)
        self._version = version

    @property
    def version(self) -> VersionIdentifierType:
        return self._version

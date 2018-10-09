from __future__ import annotations

from typing import Any, Dict, Union


class MalformedBlockstateException(Exception):
    pass


class Block:
    def __init__(
        self,
        resource_location: str,
        base_name: str,
        properties: Dict[str, Union[str, bool, int]],
    ):
        self._resource_location = resource_location
        self._base_name = base_name
        self._properties = properties
        self._blockstate = self._gen_blockstate()

    @property
    def resource_location(self) -> str:
        return self._resource_location

    @property
    def base_name(self) -> str:
        return self._base_name

    @property
    def properties(self) -> Dict[str, Union[str, bool, int]]:
        return self._properties

    @property
    def blockstate(self) -> str:
        return self._blockstate

    def _gen_blockstate(self) -> str:
        blockstate = f"{self._resource_location}:{self._base_name}"
        if self._properties:
            props = [f"{key}={value}" for key, value in self._properties.items()]
            blockstate += f"[{','.join(props)}]"
        return blockstate

    @classmethod
    def get_from_blockstate(cls, blockstate: str) -> Block:
        if ":" in blockstate:
            resource_location = blockstate[: blockstate.index(":")]
        else:
            resource_location = "unknown"

        if "[" not in blockstate:
            base_name = blockstate[blockstate.index(":") + 1 :]
            properties = {}
        else:
            if "]" not in blockstate:
                raise MalformedBlockstateException(
                    f"Blockstate has missing end bracket: {blockstate}"
                )

            base_name = blockstate[blockstate.index(":") + 1 : blockstate.index("[")]
            props = blockstate[blockstate.index("[") + 1 : blockstate.index("]")].split(
                ","
            )
            properties = {}
            for prop in props:
                key, value = prop.split("=")
                value = value.lower()

                if value in ("true", "false"):
                    properties[key] = bool(value)
                elif value.isdigit():
                    properties[key] = int(value)
                else:
                    properties[key] = value

        return cls(resource_location, base_name, properties)

    def __str__(self) -> str:
        return self._blockstate

    def __eq__(self, other: Union[Block, str]) -> bool:
        if isinstance(other, Block):
            other = other._blockstate
        return self._blockstate == other

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __hash__(self):
        return hash(self._blockstate)


class BlockManager:
    def __init__(self):
        self._name_to_block_map: Dict[str, Block] = {}
        self._block_to_index_map: Dict[Block, int] = {}

    def __getitem__(self, item: Union[Block, str]) -> int:
        if isinstance(item, str):
            item = self.get_block(item)
        return self._block_to_index_map[item]

    def get_block(self, block: str) -> Block:
        if block in self._name_to_block_map:
            return self._name_to_block_map[block]

        self._name_to_block_map[block] = b = Block.get_from_blockstate(block)
        self._block_to_index_map[b] = len(self._block_to_index_map)
        return b


if __name__ == "__main__":
    b = Block.get_from_blockstate("minecraft:air")
    d = {b: 0}
    print(b in d)
    print("minecraft:air" in d)

    manager = BlockManager()
    i1 = manager["minecraft:air"]
    i2 = manager["minecraft:stone"]
    i3 = manager["minecraft:air"]
    i4 = manager[b]
    print(i1, i2, i3, i4)

from typing import Iterable

from amulet.resource_pack.abc import BaseResourcePack as BaseResourcePack
from amulet.resource_pack.abc import BaseResourcePackManager as BaseResourcePackManager
from amulet.resource_pack.bedrock import BedrockResourcePack as BedrockResourcePack
from amulet.resource_pack.bedrock import (
    BedrockResourcePackManager as BedrockResourcePackManager,
)
from amulet.resource_pack.java import JavaResourcePack as JavaResourcePack
from amulet.resource_pack.java import JavaResourcePackManager as JavaResourcePackManager

from .unknown_resource_pack import UnknownResourcePack as UnknownResourcePack

def load_resource_pack(resource_pack_path: str) -> BaseResourcePack: ...
def load_resource_pack_manager(
    resource_packs: Iterable[str | BaseResourcePack], load: bool = True
) -> BaseResourcePackManager: ...

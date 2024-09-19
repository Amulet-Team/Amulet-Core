from typing import Iterable, Union

from amulet.resource_pack.abc import (
    BaseResourcePack,
    BaseResourcePackManager,
)
from amulet.resource_pack.java import (
    JavaResourcePack,
    JavaResourcePackManager,
)
from amulet.resource_pack.bedrock import (
    BedrockResourcePack,
    BedrockResourcePackManager,
)
from .unknown_resource_pack import UnknownResourcePack


def load_resource_pack(resource_pack_path: str) -> BaseResourcePack:
    if JavaResourcePack.is_valid(resource_pack_path):
        return JavaResourcePack(resource_pack_path)
    elif BedrockResourcePack.is_valid(resource_pack_path):
        return BedrockResourcePack(resource_pack_path)
    else:
        return UnknownResourcePack(resource_pack_path)


def load_resource_pack_manager(
    resource_packs: Iterable[Union[str, BaseResourcePack]], load: bool = True
) -> BaseResourcePackManager:
    resource_packs_out: list[BaseResourcePack] = []
    for resource_pack in resource_packs:
        if isinstance(resource_pack, str):
            resource_pack = load_resource_pack(resource_pack)
        if (
            not isinstance(resource_pack, UnknownResourcePack)
            and resource_pack.valid_pack
        ):
            if resource_packs_out:
                if isinstance(resource_pack, resource_packs_out[0].__class__):
                    resource_packs_out.append(resource_pack)
            else:
                resource_packs_out.append(resource_pack)

    resource_packs = resource_packs_out
    if resource_packs:
        if isinstance(resource_packs[0], JavaResourcePack):
            return JavaResourcePackManager(
                [pack for pack in resource_packs if isinstance(pack, JavaResourcePack)],
                load,
            )
        elif isinstance(resource_packs[0], BedrockResourcePack):
            return BedrockResourcePackManager(
                [
                    pack
                    for pack in resource_packs
                    if isinstance(pack, BedrockResourcePack)
                ],
                load,
            )

    raise NotImplementedError
    # return UnknownResourcePackManager()
